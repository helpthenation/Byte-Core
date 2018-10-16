from odoo import fields, models


class HrEmployeeTerminationReason(models.Model):
    _name = 'hr.employee.termination.reason'
    _description = 'Reason for Employment Termination'

    name = fields.Char(
        'Name',
        required=True
    )
