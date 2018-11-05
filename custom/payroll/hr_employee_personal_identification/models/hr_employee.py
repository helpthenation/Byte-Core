from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    personal_identification_ids = fields.One2many(comodel_name='hr.employee.personal.id',
                                                  inverse_name='employee_id',
                                                  string='Personal Identifications')
