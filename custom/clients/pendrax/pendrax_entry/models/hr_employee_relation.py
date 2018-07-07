from odoo import models, fields


class HrEmployeeRelation(models.Model):
    _name = 'hr.employee.relation'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)

