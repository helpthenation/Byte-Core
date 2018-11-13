from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    loan_confirmer_id = fields.Many2one('res.users', string='Loan Corfirmer')
    loan_approver_id = fields.Many2one('res.users', string='Loan Approver')
    loan_disburse_id = fields.Many2one('res.users', string='Loan Disburser')

    leave_confirmer_id = fields.Many2one('res.users', string='Loan Corfirmer')
    leave_approver_id = fields.Many2one('res.users', string='Loan Approver')
