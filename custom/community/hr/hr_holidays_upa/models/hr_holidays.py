from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.constrains('holiday_status_id')
    @api.one
    def _constrains_leave_type(self):
        company = self.env.user.company_id
        if (self.holiday_status_id.is_upa and company.upa_first_exhaust_legal
            and self.employee_id.remaining_leaves > self.number_of_days_temp):
            raise ValidationError(
                'You are requesting  UPA for %s but still have %s days of legal '
                'leaves' %
                (self.number_of_days_temp, self.employee_id.remaining_leaves))

    @api.multi
    def holidays_validate(self):
        super(HrHolidays, self).holidays_validate()

        for holiday in self:
            if (self.holiday_status_id.is_upa and self.holiday_type ==
                    'employee' and self.type == 'remove'):
                holiday.sudo()._create_deductions()

    @api.one
    def _create_deductions(self):
        if not self.holiday_status_id.is_upa:
            return

        upa_obj = self.env['hr.holidays.upa']
        deductions = upa_obj.search(
            [('holiday_id', '=', self.id)]
        )
        deductions.unlink()

        days = self.number_of_days_temp - self.employee_id.remaining_leaves

        current_period_from, current_period_to = self.holiday_status_id.ruleset_id.holidays_period(
            self.employee_id, fields.Date.from_string(self.date_from))

        next_period_from, next_period_to = self.holiday_status_id.ruleset_id.holidays_period(
            self.employee_id, fields.Date.from_string(
                self.date_from) + relativedelta(years=1))

        if days == self.number_of_days_temp:
            # we have no days in this current leave period so lets schedule all
            # deductions in the next
            upa_obj.create({
                'holiday_id': self.id,
                'days': days,
                'active_from': fields.Date.to_string(next_period_from),
                'active_to': fields.Date.to_string(next_period_to),
            })
        else:
            # we have some legal leaves in this period no let's schedule it and
            # the rest in the next
            upa_obj.create({
                'holiday_id': self.id,
                'days': days,
                'active_from': fields.Date.to_string(next_period_from),
                'active_to': fields.Date.to_string(next_period_to),
            })
            upa_obj.create({
                'holiday_id': self.id,
                'days': self.employee_id.remaining_leaves,
                'active_from': fields.Date.to_string(current_period_from),
                'active_to': fields.Date.to_string(current_period_to),
            })
