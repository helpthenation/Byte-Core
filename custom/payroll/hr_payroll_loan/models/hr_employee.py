from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    loan_count = fields.Integer(
        compute='_compute_loan_count',
        store=True,
    )
    loan_ids = fields.One2many(
        'hr.payroll.loan',
        'employee_id',
        'Active Loans',
        domain=[('state', 'in', ('draft', 'open'))]
    )
    active_loan_ids = fields.One2many(
        'hr.payroll.loan',
        'employee_id',
        'Active Loans',
        domain=[('state', '=', 'open')]
    )

    @api.one
    @api.depends('loan_ids')
    def _compute_loan_count(self):
        self = self.sudo()
        self.loan_count = len(self.loan_ids)
