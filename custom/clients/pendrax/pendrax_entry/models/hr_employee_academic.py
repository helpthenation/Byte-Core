from odoo import models, fields


class HrEmployeeAcademic(models.Model):
    _name = 'hr.employee.academic'
    _rec_name = 'employee_id'
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Employee')
    date_from = fields.Char(string='Date From')
    date_to = fields.Char(string='Date To')
    institution = fields.Many2one(comodel_name='hr.employee.institution',
                                  string='Institution')
    qualification = fields.Char(string='Qualification')

