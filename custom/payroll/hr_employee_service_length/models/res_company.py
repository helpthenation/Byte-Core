
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    contract_interval = fields.Integer(
        'Interval Between Contract (days)',
        help="Number of days between the end date of a contract and the start "
        "date of a next above which we consider it a break in employee's service length",
        default=30)
