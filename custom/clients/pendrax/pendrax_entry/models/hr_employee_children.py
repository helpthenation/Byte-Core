from odoo import models, fields,api
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class HrEmployeeChildren(models.Model):

    _name = 'hr.employee.children'
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Parent')
    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age', compute='_compute_age', readonly=True, store=True)
    date_of_birth = fields.Date(string='Date of birth', required=True)
    occupation = fields.Many2one(comodel_name='hr.children.occupation', readonly=True, string='Legacy Occupation')
    occupation_id = fields.Many2one(comodel_name='hr.occupation', string='Occupation', required=True)

    @api.multi
    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            rec.age = 0
            if rec.date_of_birth:
                start = datetime.strptime(rec.date_of_birth,
                                          DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                        DEFAULT_SERVER_DATE_FORMAT)
                age = ((end - start).days / 365)
                rec.age = age and age
