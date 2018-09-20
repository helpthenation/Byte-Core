from odoo import models, fields, api


class HrEmployeeAbsentLine(models.Model):
    _name = 'hr.employee.absent.line'
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date(string='Date', required=True)
    reason_id = fields.Many2one(comodel_name='hr.employee.absent.reason',
                                string='Reason',
                                required=True)
    days = fields.Integer(string='Days to Subtract', required=True)
    reference = fields.Char(sring='Reference',
                            compute='compute_reference')

    @api.depends('employee_id', 'employee_id')
    @api.multi
    def compute_reference(self):
        for rec in self:
            rec.reference = str(str(rec.employee_id.empid)+"/ABS/"+str(rec.date))
    __sql_constraints = [
        ('date_unique', 'unique (reference)', 'Each Date must be unique!'),
    ]
