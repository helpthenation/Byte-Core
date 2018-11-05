from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    upa_holidays_status_id = fields.Many2one(
        'hr.holidays.status',
        'UPA Leave',
    )
    upa_first_exhaust_legal = fields.Boolean(
        'First Exhaust Legal',
        help="Employee has to first exhaust legal/annual leave before UPA can "
             "be taken"
    )
