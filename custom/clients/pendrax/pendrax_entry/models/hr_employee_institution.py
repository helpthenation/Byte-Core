from odoo import models, fields


class HrEmployeeInstitution(models.Model):
    _name = 'hr.employee.institution'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)

