from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    absent_ids = fields.One2many(comodel_name='hr.employee.absent.line',
                                 inverse_name='employee_id',
                                 string='Absent Times')

    @api.multi
    def get_absent_counts(self, start, end):
        self.ensure_one()
        absents = 0
        for rec in self:
            if len(rec.absent_ids)>0:
                for line in rec.absent_ids:
                    if fields.Datetime.from_string(start) <= fields.Datetime.from_string(line.date) <= \
                            fields.Datetime.from_string(end):
                        absents += line.days
        return int(absents)

    @api.multi
    def get_days_worked(self, start, end):
        self.ensure_one()
        for rec in self:
            return 31 - rec.get_absent_counts(start, end)
