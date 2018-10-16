# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _check_date(self, cr, uid, ids, context=None):
        """
        we are overriding here because seting intervals on allocation affects
        this
        """
        for holiday in self.browse(cr, uid, ids, context=context):
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
            nholidays = self.search_count(cr, uid, domain, context=context)
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
