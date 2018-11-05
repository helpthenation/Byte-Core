# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _check_date(self):
        """
        we are overriding here because seting intervals on allocation affects
        this
        """
        for holiday in self.search([]):
            if holiday.type == 'add':
                continue
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('type', '=', 'remove'),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                return False
        return True

    @api.one
    def check_holidays(self):
        '''
        we are overriding this to ensure that leave requests are evaluated in
        their correct period
        '''
        if (self.holiday_type != 'employee' or self.type != 'remove'
                or not self.employee_id or self.holiday_status_id.limit):
            return

        dt_str = self.holiday_status_id.ruleset_id.period == 'year'\
                 and self.date_to or self.date_from

        leave_days = self.holiday_status_id.get_days(
            self.employee_id.id,
            dt=fields.Date.from_string(dt_str)
        )[self.holiday_status_id.id]
        if (leave_days['remaining_leaves'] < 0
                or leave_days['virtual_remaining_leaves'] < 0):
            # Raising a warning gives a more user-friendly feedback than the
            # default constraint error
            raise Warning('The number of remaining leaves is not sufficient  '
                          'for this leave type.\nPlease verify also the  '
                          'leaves waiting for validation.')
        return True

    @api.model
    def create(self, vals):
        status = self.env['hr.holidays.status'].browse(
            vals['holiday_status_id'])
        date_now = fields.Date.from_string(
            self.env.context.get('date_now', fields.Date.today()))

        if (not status.limit and status.ruleset_id and vals['type'] == 'add'
                and not (vals.get('date_from') and vals.get('date_to'))):
            # let's bound allocation
            period_start, period_end = status.ruleset_id.holidays_period(
                self.env['hr.employee'].browse(vals['employee_id']), date_now
            )
            vals['date_from'] = fields.Date.to_string(
                period_start) + ' 00:00:01'
            vals['date_to'] = fields.Date.to_string(period_end) + ' 23:59:59'
        return super(HrHolidays, self).create(vals)

    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!',
         ['date_from', 'date_to']),
    ]
