from odoo import models, fields, api
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta, datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    age = fields.Integer('Age', compute='_compute_age', readonly=True, store=True)

    @api.multi
    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            rec.age = 0
            if rec.birthday:
                start = datetime.strptime(rec.birthday,
                                          DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                        DEFAULT_SERVER_DATE_FORMAT)
                age = ((end - start).days / 365)
                rec.age = age and age or 10

    def compute_age(self):
        for emp in self.search([]):
            emp._compute_age()
            start = emp.emp_date and fields.Datetime.from_string(emp.emp_date).date()
            emp.emp_date = start
            con = fields.Datetime.from_string(emp.contract_id.date_start).date()
            emp.contract_id.date_start = con+timedelta(days=1)
            if start:
                emp.initial_employment_date=con-timedelta(days=1)
