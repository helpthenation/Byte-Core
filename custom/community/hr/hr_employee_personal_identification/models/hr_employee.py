from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    personal_identification_ids = fields.One2many('hr.employee.personal.id', 'employee_id', 'Personal Identifications')
