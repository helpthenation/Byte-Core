from odoo import models, fields, api


class HrEmployeePersonalIdType(models.Model):
    _name = 'hr.employee.personal.id.type'
    name = fields.Char('Identification Type', required=True,
                       index=True)
    _sql_constraints = [('name', 'UNIQUE(name)', 'Identification type already Exist')]



