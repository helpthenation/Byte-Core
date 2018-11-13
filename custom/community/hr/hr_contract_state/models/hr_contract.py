# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    state = fields.Selection(
        selection_add=[('trial_ending', 'Trail Ending')]
    )



    @api.multi
    def state_confirm(self):
        self.write({'state': 'open'})

    @api.multi
    def set_as_pending(self):
        for contract in self:
            body = '%s Contract (Ref:%s) needs to be renewed' % (
                contract.employee_id.name, contract.name)
            contract.message_post(body=body)
        return super(hr_contract, self).set_as_pending()

    @api.multi
    def set_trail_end(self):
        for contract in self:
            body = '%s Contract (Ref:%s) trial period in ending' % (
                contract.employee_id.name, contract.name)
            contract.message_post(body=body)


            hr_users = self.env['res.users'].search(
                [('groups_id', 'in', (self.env.ref('hr.group_hr_user').id,))])
            if hr_users:
                contract.message_subscribe_users(user_ids=hr_users.ids)

            # let's send an email notifying people about this
            try:
                mail_template = self.env.ref(
                    'hr_contract_state.trial_end_email')
                if mail_template:
                    mail_template.send_mail(contract.id)
            except Exception as e:
                _logger.exception()
        return self.write({'state': 'trial_ending'})

    @api.multi
    def send_expiry_notification(self, days):
        self.ensure_one()
        for rec in self:
            mail_object = self.env['mail.mail']
            subject = rec.id_type.name + " about to expire"
            message = "This is to notify you that " + \
                      rec.employee_id.name + "'s " + \
                      rec.id_type.name + " will expire in " + str(days) + " days time. Expiry date is " + str(
                rec.expiry_date)
            user = self.env.user
            default_email = self.notify_employee_id.work_email
            email = mail_object.create({'subject': subject,
                                        'email_from': user.company_id.email,
                                        'email_to': default_email and default_email,
                                        'body_html': message})
            email.send()

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(
            hr_contract,
            self).message_get_suggested_recipients()
        try:
            for contract in self:
                # all hr users
                # let's subscribe hr_users
                hr_users = self.env['res.users'].search([('groups_id', 'in', (
                    self.env.ref('hr.group_hr_user').id,))])
                if hr_users:
                    for user in hr_users:
                        contract._message_add_suggested_recipient(
                            recipients, partner=user.partner_id,
                            reason=_('HR User'))

                if contract.employee_id.parent_id and contract.employee_id.parent_id.work_email:
                    contract._message_add_suggested_recipient(
                        recipients,
                        email=contract.employee_id.parent_id.work_email,
                        reason=_('Supervisor Email'))

                if (
                    contract.employee_id.department_id and contract.employee_id.department_id.manager_id
                        and contract.employee_id.department_id.manager_id.work_email):
                    contract._message_add_suggested_recipient(
                        recipients,
                        email=contract.employee_id.department_id.manager_id.work_email,
                        reason=_('Supervisor Email'))
        except AccessError:  # no read access rights -> ignore suggested recipients
            pass
        return recipients

    @api.multi
    def try_check_expiry(self):
        for rec in self.search([('state','=', 'open')]):
            if rec.trial_date_end and rec.trial_date_end:
                days = relativedelta(
                    fields.Date.from_string(rec.trial_date_end),
                    fields.Date.from_string(fields.Date.today())).days
                if 30 >= days > 0:
                    rec.set_trail_end()


