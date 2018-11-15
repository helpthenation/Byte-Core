from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    loan_confirmer_id = fields.Many2one('hr.employee', string='Loan Corfirmer')
    loan_approver_id = fields.Many2one('hr.employee', string='Loan Approver')
    loan_disburse_id = fields.Many2one('hr.employee', string='Loan Disburser')

    leave_confirmer_id = fields.Many2one('hr.employee', string='Leave Corfirmer')
    leave_approver_id = fields.Many2one('hr.employee', string='Leave Approver')
    leave_allowance_disburser_id = fields.Many2one('hr.employee', string='Leave Allowance Disburser')
