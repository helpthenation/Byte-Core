# -*- coding: utf-8 -*-

from datetime import date

from odoo import models, fields, api


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    ruleset_id = fields.Many2one(
        'hr.holidays.evaluation.ruleset',
        'Allocation Evaluation Ruleset',
        help="Allocation Evaluation Ruleset to be used by this holiday type.",
    )
    ruleset_method = fields.Selection(
        [
            ('automate', 'Automated'),
            ('manual', 'Manual'),
        ],
        string='Allocation Method',
        related='ruleset_id.method',
        readonly=True,
        store=True,
    )

    @api.multi
    def get_days(self, employee_id, dt=None):
        self = self.sudo()
        dt = dt or self.env.context.get('date_now', date.today())
        if not isinstance(dt, date):
            dt = fields.Date.from_string(dt)
        result = dict(
            (id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                      virtual_remaining_leaves=0))
            for id in self.ids
        )

        employee = self.env['hr.employee'].browse(employee_id)
        holiday_obj = self.env['hr.holidays']
        for status in self:
            ruleset = status.ruleset_id
            if not ruleset or status.limit:
                continue
            if ruleset.period == 'anniversary' and not employee.date_start:
                # how can we fail gracefully yet let user know why
                continue
            result[status.id]['max_leaves'] = ruleset.evaluate_allocation(
                employee, dt=dt, status=status)
            result[status.id]['leaves_taken'] = ruleset.evaluate_withdrawals(
                status, employee, dt=dt)
            result[status.id]['remaining_leaves'] = (
                result[status.id]['max_leaves']
                + result[status.id]['leaves_taken']
            )

            # let gather ones waiting validation in this period
            # if employee employment date in the future
            if employee.date_start > fields.Date.to_string(dt):
                return result
            period_start, period_end = ruleset.holidays_period(employee, dt)
            pending_validation = holiday_obj.search(
                [
                    ('employee_id', '=', employee.id),
                    ('state', 'in', ('validate1', 'confirm')),
                    ('holiday_status_id', '=', status.id),
                    ('date_from', '>=', str(period_start)),
                    ('date_from', '<=', str(period_end)),
                    ('type', '=', 'remove'),
                    ('holiday_type', '=', 'employee')
                ]
            ).mapped('number_of_days')
            result[status.id]['virtual_remaining_leaves'] = (
                result[status.id]['remaining_leaves']
                + sum(pending_validation)
            )
        return result

    @api.model
    def cron_update_allocation(self):
        self.search([]).update_allocation()

    @api.multi
    def update_allocation(self):
        employees = self.env['hr.employee'].search([])

        for status in self.filtered(
                lambda r: r.ruleset_id and r.ruleset_id.method == 'manual'):
            for employee in employees:
                auto_allocation = status.ruleset_id.evaluate_allocation_automate(
                    employee, status)
                manual_allocation = status.ruleset_id.evaluate_allocation_manual(
                    employee, status)
                days = auto_allocation - manual_allocation
                if days != 0:
                    status._update_allocation_record(employee, days)

    def _create_manual_allocation(self, employee, days):
        self.ensure_one()
        holiday = self.env['hr.holidays'].create({
            'name': 'Automatically Added Allocation',
            'type': 'add',
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': self.id,
            'number_of_days_temp': days,
        })
        for sig in ('confirm', 'validate', 'second_validate',):
            holiday.signal_workflow(sig)
        return holiday

    def _update_allocation_record(self, employee, days):
        self.ensure_one()
        period_start, period_end = self.ruleset_id.holidays_period(employee)
        allocations = self.env['hr.holidays'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('holiday_status_id', '=', self.id),
            ('type', '=', 'add'),
            ('date_from', '<=', str(period_end)),
            ('date_to', '>=', str(period_start)),
        ])

        if not allocations and days > 0:  # do not have any allocation at this time
            self._create_manual_allocation(employee, days)
        elif allocations and days > 0:  # we need to add to an allocation so we can just throw untop of the fist
            allocations[0].number_of_days_temp += days
        elif allocations and days < 0:
            # let's first make sure we do not take away so much allocation that
            # we have more remove leaves
            remaining_leaves = self.get_days(employee.id)[self.id][
                'remaining_leaves']
            days = min(abs(remaining_leaves), abs(days))
            for allocation in allocations:
                if days > allocation.number_of_days_temp:  # we have
                    days -= allocation.number_of_days_temp
                    allocation.signal_workflow('refuse')
                    allocation.signal_workflow('reset')
                    allocation.unlink()
                    if days == 0:
                        break
                else:
                    allocation.number_of_days_temp -= days
                    break
