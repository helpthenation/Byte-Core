from datetime import date

from odoo import models, fields, api


class HrHolidaysEvaluationRuleset(models.Model):
    _inherit = 'hr.holidays.evaluation.ruleset'

    @api.multi
    def evaluate_withdrawals(self, holiday_status, employee, dt=None):

        self.ensure_one()
        dt = dt or date.today()
        # if employee employment date in the future
        if employee.date_start > fields.Date.to_string(dt):
            return 0

        days = super(HrHolidaysEvaluationRuleset, self).evaluate_withdrawals(
            holiday_status, employee, dt=dt)

        upa_obj = self.env['hr.holidays.upa']
        legal_leave = employee.company_id.legal_holidays_status_id

        upa_days = 0
        if legal_leave in holiday_status:
            upa_days = upa_obj.sudo().get_outstanding(
                employee.id, fields.Date.to_string(dt))
            upa_days = (upa_days > 0) and (upa_days * -1) or upa_days

        return days + upa_days
