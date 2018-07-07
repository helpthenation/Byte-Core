from odoo import models, fields


class HrEmployeeReligion(models.Model):
    _name = 'hr.employee.religion'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)

