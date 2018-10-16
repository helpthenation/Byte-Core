# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 215 Salton Massally (<smassally@idtlabs.sl>).
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
import calendar
from datetime import date, timedelta

from odoo import models, fields, api
from odoo.exceptions import Warning as UserWarning


class HrHolidaysEvaluationRuleset(models.Model):
    _name = 'hr.holidays.evaluation.ruleset'

    name = fields.Char(required=True)
    mode = fields.Selection(
        [
            ('first', 'First'),
            ('max', 'Largest'),
            ('min', 'Minimum')
        ],
        'Evaluation Mode',
        default='first',
        required=True,
        help="Defines what to do if multiple rules in this ruleset evaluates "
             "to true.\n * Consider only the first to evaluate.\n * Consider "
             "the one with the largest return value.\n * COnsider the one "
             "with the smallest return value."
    )
    period = fields.Selection(
        [
            ('year', 'Yearly'),
            ('fiscal', 'Fiscal Year (Pay Period)'),
            ('anniversary', 'Employment Anniversary'),
        ],
        'Period Definition',
        default='year',
        required=True,
        help="Defines what concept of leave period should be used for "
             "tracking taken holidays.\n * Start of the year will consider "
             "every new year as the start of a new leave period.\n *  "
             "Employment Anniversary will use the anniversary of employee's "
             "employment"
    )
    period_year_granular = fields.Selection(
        [
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
            ('half-year', 'Half Yearly'),
            ('year', 'Yearly')
        ],
        'Yearly Granularity',
        default='year',
    )
    method = fields.Selection(
        [
            ('automate', 'Automated'),
            ('manual', 'Manual'),
        ],
        string='Allocation Method',
        default='automate'
    )
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many(
        'hr.holidays.evaluation.rule',
        'ruleset_id',
        'Allocation Rules'
    )

    @api.multi
    def evaluate_allocation(self, employee, status, dt=None):
        """
        evaluates employee's maximum allocation at a given time
        @param employee: employee for whom we need to evaluate allocation
        @param dt: date object that allows also to compute allocation at a
                   point in time rather than just now
        """
        self.ensure_one()
        dt = dt or date.today()

        if self.method == 'automate':
            # let's pass this in so that employee service length is computed
            # at our reference date
            return self.evaluate_allocation_automate(employee, status, dt=dt)
        else:
            # just like removals we want to be able to bound allocations
            return self.evaluate_allocation_manual(employee, status, dt=dt)

    @api.multi
    def evaluate_allocation_automate(self, employee, status, dt=None):
        """
        evaluates employee's maximum allocation at a given time
        @param employee: employee for whom we need to evaluate allocation
        @param dt: date object that allows also to compute allocation at a
                   point in time rather than just now
        """
        self.ensure_one()
        dt = dt or date.today()

        # let's pass this in so that employee service length is computed
        # at our reference date
        employee = employee.with_context(date_now=dt)
        localdict = dict(
            employee=employee,
            contract=employee.contract_id,
            job=employee.job_id,
            date_ref=dt,
            result=None,
            holiday_status=status,
            company=employee.company_id
        )
        rules_matched_days = []
        for rule in self.rule_ids:
            if rule.satisfy_condition(localdict):
                rules_matched_days.append(rule.amount)
                if self.mode == 'first':
                    break
        if not rules_matched_days:
            return 0
        if self.mode == 'min':
            return min(rules_matched_days)
        elif self.mode == 'max':
            return max(rules_matched_days)
        else:
            return rules_matched_days[0]

    @api.multi
    def evaluate_allocation_manual(self, employee, status, dt=None):
        """
        evaluates employee's maximum allocation at a given time
        @param employee: employee for whom we need to evaluate allocation
        @param dt: date object that allows also to compute allocation at a
                   point in time rather than just now
        """
        self.ensure_one()
        dt = dt or date.today()

        # just like removals we want to be able to bound allocations
        period_start, period_end = self.holidays_period(employee, dt)
        allocations = self.env['hr.holidays'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('holiday_status_id', '=', status.id),
            ('type', '=', 'add'),
            ('date_from', '<=', str(period_end)),
            ('date_to', '>=', str(period_start)),
        ])
        return sum(allocations.mapped('number_of_days_temp'))

    @api.multi
    def evaluate_withdrawals(self, holiday_status, employee, dt=None):
        """
        evaluates number of leaves taken in a given period
        @param holiday_status: holiday status to evaluate for
        @param employee: employee for whom we need to evaluate withdrawals
        @param dt: date object that allows also to compute withdrawals at a
                   point in time rather than just now
        """

        self.ensure_one()
        dt = dt or date.today()
        # if employee employment date in the future
        if employee.date_start > fields.Date.to_string(dt):
            return 0
        period_start, period_end = self.holidays_period(employee, dt)
        domain = [
            ('state', '=', 'validate'),
            ('date_from', '>=', str(period_start)),
            ('date_from', '<=', str(period_end)),
            ('type', '=', 'remove'),
            ('employee_id', '=', employee.id),
            ('holiday_status_id', '=', holiday_status.id)
        ]
        leaves = self.env['hr.holidays'].search(domain)
        return sum(leaves.mapped('number_of_days'))

    @api.multi
    def evaluate_remaining(self, employee, dt=None):
        """
        self.ensure_one()
        evaluates how much leave employee is entitled to
        @param employee: employee for whom we need to evaluate remaining
        @param dt: date object that allows also to compute remaining at a
                   point in time rather than just now
        """
        dt = dt or date.today()
        return (self.evaluate_allocation(employee, dt) -
                self.evaluate_withdrawals(employee, dt))

    @api.multi
    def holidays_period(self, employee, dt=None):
        """
        Calculates the start and end date of an employee's leave period taking
        into consideration this ruleset's definition of that a leave period is
        @param employee: employee object
        @param dt: if supplied it gives the leave period pounding that date
        @return: tuple of date objects (period_start, period_end)
        """
        self.ensure_one()
        dt = dt or date.today()
        if self.period == 'anniversary':
            employee_start_dt = fields.Date.from_string(employee.date_start)
            if employee_start_dt and employee_start_dt > dt:
                raise UserWarning('Reference date should not be before '
                                  'employee\'s employment date')
            one_day_before = employee_start_dt - timedelta(days=1)
            if one_day_before.month == 2 and one_day_before.day == 29 and not calendar.isleap(
                    dt.year + 1):
                one_day_before_day = 28
            else:
                one_day_before_day = one_day_before.day
            return (
                date(dt.year, employee_start_dt.month, employee_start_dt.day),
                date(dt.year + 1, one_day_before.month, one_day_before_day)
            )
        elif self.period == 'fiscal':
            # let's get the correct fiscal year to use
            date_str = fields.Date.to_string(dt)
            domain = [
                ('date_start', '<=', date_str),
                ('date_stop', '>=', date_str),
                ('company_id', '=', employee.company_id.id),
                ('schedule_pay', '=', employee.contract_id.schedule_pay),
            ]
            fiscal_year = self.env['hr.fiscalyear'].search(domain, limit=1)

            if not fiscal_year:
                raise UserWarning(
                    'Leave evaluation failed as fiscal year could not be determined'
                )

            return (
                fields.Date.from_string(fiscal_year.date_start),
                fields.Date.from_string(fiscal_year.date_stop),
            )
        elif self.period == 'year':
            if self.period_year_granular == 'half-year':
                halfyear_map = {
                    1: ((1, 1), (6, 30)),
                    2: ((7, 1), (12, 31)),
                }
                index = dt.month <= 6 and 1 or 2
                return (date(dt.year, halfyear_map[index][0][0],
                             halfyear_map[index][0][1]),
                        date(dt.year, halfyear_map[index][1][0],
                             halfyear_map[index][1][1]))
            elif self.period_year_granular == 'quarter':
                quarter_map = {
                    1: ((1, 1), (3, 31)),
                    2: ((4, 1), (6, 30)),
                    3: ((7, 1), (9, 30)),
                    4: ((10, 1), (12, 31))
                }
                quarter = (dt.month - 1) // 3 + 1
                return (date(dt.year, quarter_map[quarter][0][0],
                             quarter_map[quarter][0][1]),
                        date(dt.year, quarter_map[quarter][1][0],
                             quarter_map[quarter][1][1]))
            elif self.period_year_granular == 'month':
                return date(dt.year, dt.month, 1), date(dt.year, dt.month,
                                                        calendar.monthrange(
                                                            dt.year, dt.month)[
                                                            1])
            else:
                return date(dt.year, 1, 1), date(dt.year, 12, 31)
