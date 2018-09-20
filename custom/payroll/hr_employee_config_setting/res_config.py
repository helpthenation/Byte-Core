from odoo import models


class HrEmployeeConfiguration(models.TransientModel):
    _name = 'hr.employee.config.settings'
    _inherit = 'res.config.settings'
