from odoo import models, fields


class HrEmployeeChildren(models.Model):

    _name = 'hr.employee.children'
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Parent')
    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    occupation = fields.Many2one(comodel_name='hr.children.occupation', string='Occupation')
