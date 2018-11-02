from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    first_approver_id = fields.Many2one(comodel_name='hr.employee', string='PayrollAproval by')

