from odoo import models, fields


class HrEmployeeTribe(models.Model):
    _name = 'hr.employee.tribe'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)

