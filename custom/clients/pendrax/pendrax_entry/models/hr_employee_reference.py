from odoo import models, fields


class HrEmployeeReference(models.Model):
    _name = 'hr.employee.reference'
    _rec_name = 'employee_id'
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Employee')
    name = fields.Char(string='Name', required=True)
    address = fields.Char(string='Work Address', required=True)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email')
    occupation_id = fields.Many2one(comodel_name='hr.occupation', string='Occupation', required=True)
