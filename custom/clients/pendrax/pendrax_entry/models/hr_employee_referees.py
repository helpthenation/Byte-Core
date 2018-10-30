from odoo import models, fields


class HrEmployeeReferee(models.Model):
    _name = 'hr.employee.referee'
    _rec_name = 'employee_id'
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Employee')
    name = fields.Char(string='Name', required=True)
    photo = fields.Binary('Photo', required=True)
    address = fields.Char(string='Home Address', required=True)
    address0 = fields.Char(string='Work Address', required=True)
    occupation = fields.Char(string='Legacy Occupation', readonly=True)
    occupation_id = fields.Many2one(comodel_name='hr.occupation', string='Occupation', required=True)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email')
