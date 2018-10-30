from odoo import models, fields


class HrEmployeeHistory(models.Model):
    _name = 'hr.employee.history'
    _rec_name = 'employee_id'
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Employee')
    date_from = fields.Char(string='Date From', required=True)
    date_to = fields.Char(string='Date To', required=True)
    name = fields.Char(string='Name', required=True)
    place_id = fields.Many2one(comodel_name='hr.employee.work.place',
                               string='Work Place', required=True)
    position = fields.Char(string='Legacy Position', readonly=True)
    salary = fields.Float(string='Salary', required=True)
    occupation_id = fields.Many2one(comodel_name='hr.occupation', string='Position', required=True)
