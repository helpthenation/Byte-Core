from odoo import models, fields


class HrEmployeeAbsentReason(models.Model):
    _name = 'hr.employee.absent.reason'
    name = fields.Char(string='Name',
                       required=True)
    days = fields.Integer(string='Days to Subtract',
                          required=True)
    note = fields.Text(string="Note")
