
import operator
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    initial_employment_date = fields.Date(
        help='Date of first employment if it was before the start of the '
             'first contract in the system.',
        track_visibility='onchange'
    )
    date_start = fields.Date(
        'Start Date',
        readonly=True,
        compute='_compute_service_details'
    )
    length_of_service = fields.Float(
        'Length of Service',
        readonly=True,
        compute='_compute_employment_length',
        help="Service length in years"
    )
    length_of_service_str = fields.Char(
        'Length of Service',
        readonly=True,
        compute='_compute_employment_length'
    )

    def _first_contract(self):
        return self.contract_ids \
            .sorted(key=operator.itemgetter('date_start', 'id'))[0]

    @api.multi
    @api.constrains('initial_employment_date', 'contract_ids')
    def _check_initial_employment_date(self):
        self.ensure_one()
        for rec in self:
            rec = rec.sudo()
            if rec.initial_employment_date and len(rec.contract_ids):
                initial_dt = fields.Date.from_string(rec.initial_employment_date)
                first_contract_dt = fields.Date.from_string(
                    rec._first_contract().date_start)
                if initial_dt > first_contract_dt:
                    raise ValidationError("The initial employment date cannot be "
                                          "after the first contract in the system")

    @staticmethod
    def _get_contract_interval(contract, dt_ref=None):
        if not dt_ref:
            dt_ref = date.today()
        end_date = dt_ref
        if contract.date_end:
            end_date = fields.Date.from_string(contract.date_end)
            if end_date >= dt_ref:
                end_date = dt_ref

        # stops us from returning negative relativedelta... e.g in cases where
        # we wish to import old leaves
        contract_start = fields.Date.from_string(contract.date_start)
        if contract_start > end_date:
            return relativedelta()
        else:
            return relativedelta(end_date, contract_start)

    def get_service_length_delta_at_time(self, dt=None):
        '''
        get's the service length for an employee at a specific date
        '''
        if not self.date_start:
            return False
        if not dt:
            dt_today = date.today()
        else:
            dt_today = isinstance(dt, date) and dt \
                or fields.Date.from_string(dt)
        dt_date_start = fields.Date.from_string(self.date_start)
        if dt_date_start > dt_today:
            return False
        delta = relativedelta(dt_today, dt_today)
        if not len(self.contract_ids):  # if employee has no contracts
            delta = relativedelta(dt_today, dt_date_start)
        else:
            # if employee has contracts let's first find the months for which
            # employee has been employed according to the contracts

            # First get the delta between earliest contract start date and latest
            # contract end date
            contracts_sorted = self.contract_ids.sorted(
                key=operator.itemgetter('date_start', 'id'))
            earliest_start = fields.Date.from_string(
                contracts_sorted[0].date_start)
            lastest_end = contracts_sorted[
                -1].date_end and fields.Date.from_string(
                contracts_sorted[-1].date_end) or dt_today

            # if the end date is in the future we want to ensure that we use
            # the present date
            lastest_end = lastest_end > dt_today and dt_today or lastest_end
            delta = relativedelta(lastest_end, earliest_start)

            # The account for possible breaks in the contract
            # end date of previous + threshold < start date of next
            company = self.company_id or self.env.user.company_id
            threshold = company.contract_interval or 30
            pointer = 0
            while pointer < (len(contracts_sorted) - 1):
                end_date = contracts_sorted[
                    pointer].date_end and fields.Date.from_string(
                    contracts_sorted[pointer].date_end) or False
                next_start_date = fields.Date.from_string(
                    contracts_sorted[pointer + 1].date_start)

                if end_date and (
                    end_date + timedelta(
                        days=threshold) < next_start_date):
                    delta -= relativedelta(next_start_date, end_date)

                pointer += 1

            # if initial employment date is before the first contract date then
            # let's take the difference into account
            if self.date_start == self.initial_employment_date:
                first_contract_dt = fields.Date.from_string(
                    self._first_contract().date_start)
                delta += relativedelta(first_contract_dt, dt_date_start)

        if delta:
            days = delta.days % 30
            months = delta.months + int(delta.days / 30)
            years = delta.years + int(months / 12)
            months = months % 12
            return relativedelta(years=years, months=months, days=days)
        return False

    @api.one
    @api.depends('contract_ids', 'initial_employment_date',
                 'contract_ids.date_start', 'contract_ids.employee_id')
    def _compute_service_details(self):
        user = self.env.uid
        self = self.sudo()
        if not len(self.contract_ids):
            if not self.initial_employment_date:
                return
            else:
                date_start = self.initial_employment_date
        else:
            first_contract = self._first_contract()
            date_start = first_contract.date_start
            if self.initial_employment_date \
                    and fields.Date.from_string(first_contract.date_start) \
                > fields.Date.from_string(
                        self.initial_employment_date):
                date_start = self.initial_employment_date
        self = self.sudo(user)
        self.date_start = date_start

    @staticmethod
    def _convert_timedelta_to_str(delta):
        str_since = ''
        year_label = delta.years > 1 and 'yrs' or 'yr'
        month_label = delta.months > 1 and 'mnths' or 'mnth'
        year_str = month_str = ''
        if delta.years:
            year_str = '%s %s' % (delta.years, year_label)

        if delta.months:
            month_str = '%s %s' % (delta.months, month_label)

        str_since += year_str
        if year_str and month_str:
            str_since += ' and ' + month_str
        elif month_str:
            str_since += month_str
        return str_since

    @api.one
    @api.depends('contract_ids', 'initial_employment_date',
                 'contract_ids.date_start', 'contract_ids.employee_id')
    def _compute_employment_length(self):
        '''
        employment length inn years
        '''
        dt = ('date_now' in self.env.context and self.env.context['date_now']
              or fields.Date.today())

        delta = self.sudo().get_service_length_delta_at_time(dt)
        if not delta:
            return 0.0
        self.length_of_service = delta.years + (delta.months / 12.0) + (
            delta.days / 365.25)
        self.length_of_service_str = self._convert_timedelta_to_str(delta)
