from odoo import models, fields, api


class HrEmployeeReference(models.Model):
    _name = 'hr.employee.reference'
    _rec_name = 'employee_id'
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Employee')
    name = fields.Char(string='Name', )
    address = fields.Char(string='Work Address', )
    phone = fields.Char(string='Phone', )
    email = fields.Char(string='Email')
    occupation_id = fields.Many2one(comodel_name='hr.occupation', string='Occupation', )
