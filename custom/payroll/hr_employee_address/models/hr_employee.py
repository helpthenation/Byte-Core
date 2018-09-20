from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    address = fields.Char(string='Residential Address',
                          help='Residential Address of employee')
