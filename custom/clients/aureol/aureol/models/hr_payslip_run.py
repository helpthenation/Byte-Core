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
    aureol_staff_category = fields.Selection([('general', 'General staff'),
                                              ('management', 'Management staff')],
                                             string='Staff Category',
                                             required=True)
    first_approver_id = fields.Many2one(comodel_name='hr.employee', string='Payroll Aproval by: ', required=True)
    same_gross = fields.Boolean(string='Same Gross', help='Same GROSS since start of FY')
    same_paye = fields.Boolean(string='Same Paye', help='Same PAYE since start of FY')

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
            if len(run.slip_ids)<1:
                raise ValidationError('Cannot Send a blank payroll for approval. Please Generate some payslips by clicking the Generate Payslips button')
            if not run.first_approver_id.work_email:
                raise UserError(_("Cannot send email: Approver %s has no email address.") % run.first_approver_id.name)
            template.with_context(lang=self.env.user.lang).send_mail(run.id, force_send=True, raise_exception=True)
            #_logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            self.write({'state': 'request'})


    @api.multi
    def get_payslip_employees_wizard(self):
        """ Replace the static action used to call the wizard
        """
        self.ensure_one()
        if self.aureol_staff_category=='management' and not self.user_has_groups('hr_payroll.group_hr_payroll_manager'):
            raise ValidationError('Sorry! You are not allowed to generate payroll for Management Staff')
        view = self.env.ref('hr_payroll.view_hr_payslip_by_employees')

        company = self.company_id

        employee_obj = self.env['hr.employee']

        employee_ids = employee_obj.search(
            [('aureol_staff_category', '=', self.aureol_staff_category)]).ids

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Payslips'),
            'res_model': 'hr.payslip.employees',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_company_id': company.id,
                'default_schedule_pay': self.schedule_pay,
                'default_employee_ids': [(6, 0, employee_ids)],
            }
        }