#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import requests


import babel

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    first_approver_id = fields.Many2one(comodel_name='hr.employee', string='Payroll Aproval by: ', required=True)

    '''
    @api.multi
    def set_to_request(self):
        self.write({'state': 'request'})
        self.ensure_one()

        template = self.env.ref('hr_payroll.payroll_email_template')
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form')
        self = self.with_context(
            default_model='hr.payslip.run',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='mass_mail',
            default_email_from=self.company_id.email,
            mark_so_as_sent=True,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': self.env.context,
        }



    @api.multi
    def set_to_request(self):
        self.ensure_one()

        template = self.env.ref('hr_payroll.payroll_email_template')
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.write({'state': 'request'})
    '''

    @api.multi
    def set_to_request(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = self.now(days=+30)

        self.approval_prepare(expiration=expiration)

        # send email to users with their signup url
        template = self.env.ref('hr_payroll.payroll_email_template')
        assert template._name == 'mail.template'
        for run in self:
            if not run.first_approver_id.work_email:
                raise UserError(_("Cannot send email: Approver %s has no email address.") % run.first_approver_id.name)
            template.with_context(lang=self.env.user.lang).send_mail(run.id, force_send=True, raise_exception=True)
            #_logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            self.write({'state': 'request'})