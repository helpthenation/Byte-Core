
import logging
from datetime import datetime, timedelta, time

from dateutil.rrule import rrule, YEARLY

from odoo import models, fields, api
from odoo.exceptions import Warning as UserWarning

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    allowance_line_ids = fields.One2many(
        'hr.payroll.allowance.line',
        'contract_id',
        'Allowances',
        copy=True,
    )

    @api.multi
    def alw_amount_python_compute(self, slip, code):
        self.ensure_one()
        contract = self[0]
        employee = contract.employee_id

        if not employee.date_start:
            raise UserWarning('Employee %s does not have an initial date '
                              'of employment' % (employee.name))
        line = contract.allowance_line_ids.filtered(
            lambda r: r.code == code)
        alw = line.allowance_id
        # default unit and units.. this case matches what we expect if this
        # allowance is being paid at every slip
        unit = 1
        unit_amount = line.amount
        if alw.interval == 'yearly':
            dtCmpStart = fields.Date.from_string(slip.date_from)
            dtCmpEnd = fields.Date.from_string(slip.date_to)
            dtEmpStart = fields.Date.from_string(employee.date_start)

            if alw.yearly_payment_strategy == 'anniversary':
                # if we should pay on anniversary and if this is the employee
                # anniversary then let's multiply the amount by 12...
                # we are assuming that the monthly amount is what is recorded
                # on the contract
                employee = employee.with_context(
                    date_now=fields.Date.to_string(dtCmpEnd))
                if employee.length_of_service > 1.0:
                    rr = rrule(YEARLY,
                               dtstart=(dtEmpStart + timedelta(days=1)))
                    recurringDates = rr.between(
                        datetime.combine(dtCmpStart, time.min),
                        datetime.combine(dtCmpEnd, time.max),
                        inc=True
                    )
                    if len(recurringDates):
                        unit = 12
                    else:
                        unit = 0.0
                        unit_amount = 0.0
            elif alw.yearly_payment_strategy == 'yearly':
                if dtCmpStart.month == 1:
                    # we are paying at the start of the year and we happen to
                    # be in the firstg month
                    unit = 12
                else:
                    if (dtEmpStart >= dtCmpStart and dtEmpStart < dtCmpEnd and
                            alw.yearly_payment_prorate):
                        # employee is joining and we are being asked to prorate
                        # employee's pay over the remaining month in the year
                        unit = 12 - dtCmpStart.month + 1
                    else:
                        unit = 0.0
                        unit_amount = 0.0
        return unit_amount * unit

    @api.multi
    def alw_condition_python(self, slip, code):
        self.ensure_one()
        contract = self
        employee = contract.employee_id
        if not employee.date_start:
            raise UserWarning('Employee %s does not have an initial date '
                              'of employment' % (employee.name))
        alw_obj = self.env['hr.payroll.allowance']
        allowances = alw_obj.search([('code', '=', code)])

        if not len(allowances):
            _logger.error(
                'Allowance Category with code %s was not found' % (code))
            return False
        if code not in contract.allowance_line_ids.mapped('code'):
            # alw does nto apply to contract
            return False
        line = contract.allowance_line_ids.filtered(
            lambda r: r.code == code)
        alw = line.allowance_id
        if alw.interval == 'each':
            # if this allowance is being paid each month then it is clearly
            # simple, let's return True
            return True
        elif alw.interval == 'yearly':
            dtCmpStart = fields.Date.from_string(slip.date_from)
            dtCmpEnd = fields.Date.from_string(slip.date_to)
            dtEmpStart = fields.Date.from_string(employee.date_start)
            if alw.yearly_payment_strategy == 'anniversary':
                # we pay whenever it is the anniversary of employees
                employee = employee.with_context(
                    date_now=fields.Date.to_string(dtCmpEnd))
                if employee.length_of_service > 1.0:
                    rr = rrule(
                        YEARLY, dtstart=(dtEmpStart + timedelta(days=1)))
                    recurringDates = rr.between(
                        datetime.combine(dtCmpStart, time.min),
                        datetime.combine(dtCmpEnd, time.max),
                        inc=True
                    )
                    if len(recurringDates):
                        return True
                    else:
                        return False
            elif alw.yearly_payment_strategy == 'yearly':
                if dtCmpStart.month == 1:  # we pay at the start of the year
                    return True
                elif alw.yearly_payment_prorate:
                    # not start of the year but we prorate because we are being
                    # asked to
                    return True
        return False
