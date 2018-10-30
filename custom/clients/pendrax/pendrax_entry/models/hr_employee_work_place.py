from odoo import models, fields


class HrEmployeeWorkPlace(models.Model):
    _name = 'hr.employee.work.place'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)

