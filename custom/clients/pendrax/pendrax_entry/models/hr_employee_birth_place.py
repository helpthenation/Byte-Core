from odoo import models, fields


class HrEmployeeBirthPlace(models.Model):
    _name = 'hr.employee.birthplace'
    _rec_name = 'name'
    name = fields.Char(string='Name')

