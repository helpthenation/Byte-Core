# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HrPayrollConfigSettings(models.TransientModel):
    _name = 'hr.payroll.config.settings'
    _inherit = 'res.config.settings'

    module_hr_payroll_account = fields.Boolean(string='Link your payroll to accounting system',
        help="Create journal entries from payslips")
    '''
    first_approver_id = fields.Many2one(comodel_name='hr.employee', string='Payroll Aproval by: ')

    @api.model
    def get_default_company_values(self, fields):
        company = self.env.user.company_id
        return {
            'first_approver_id': company.first_approver_id.id,
        }

    @api.one
    def set_company_values(self):
        company = self.env.user.company_id
        company.first_approver_id = self.first_approver_id
    '''