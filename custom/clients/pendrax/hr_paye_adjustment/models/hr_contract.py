from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    paye_adjustment = fields.Float(string='PAYE Adjustment',
                                   help='Adjustment for PAYE')