from odoo import models, fields


class HrEmployeeHistory(models.Model):
    _name = 'hr.employee.history'
    _rec_name = 'employee_id'
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Employee')
    date_from = fields.Char(string='Date From')
    date_to = fields.Char(string='Date To')
    name = fields.Char(string='Name')
    place_id = fields.Many2one(comodel_name='hr.employee.work.place',
                               string='Work Place')
    position = fields.Char(string='Position')
    salary = fields.Float(string='Salary')
