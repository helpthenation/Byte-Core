from odoo import models


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _order = "date_start asc, id asc"
