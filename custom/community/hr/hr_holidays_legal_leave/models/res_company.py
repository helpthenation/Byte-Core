from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    legal_holidays_status_id = fields.Many2one(
        'hr.holidays.status',
        'Legal Leave Status',
    )
