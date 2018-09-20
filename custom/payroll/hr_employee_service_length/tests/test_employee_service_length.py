from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestEmployeeServiceLength(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeServiceLength, self).setUp()
        self.contract_model = self.env["hr.contract"]
        self.employee_model = self.env['hr.employee']

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        dt = date.today() - relativedelta(months=6)
        self.six_months_ago = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

        dt = date.today() - relativedelta(years=1)
        self.one_year_ago = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

        dt = date.today() - relativedelta(years=2)
        self.two_year_ago = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

        dt = date.today() - relativedelta(years=3)
        self.three_year_ago = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

        dt = date.today() + relativedelta(years=1)
        self.one_year_in_future = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

        self.now = date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)

    def test_initial_employment_date_only_supplied(self):
        # if we are supplying only the initial employment date that should
        # be used to calculate service length
        self.employee.write({'initial_employment_date': self.one_year_ago})
        self.assertAlmostEqual(self.employee.length_of_service, 1.0)

    def test_contract_start_date_only_supplied(self):
        # initial employment date not supplied but we do have a contract
        # start date
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.one_year_ago,
                'date_end': self.one_year_in_future,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 1.0)

    def test_inital_employment_before_first_contract_date(self):
        # initial employment date is supplied and we have a contract
        # however in this case the initial employment date is before that
        # of the first contract... we expect to use initial employment date
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.one_year_ago,
                'date_end': self.one_year_in_future,
                'wage': 5000
            }
        )
        self.employee.write({'initial_employment_date': self.two_year_ago})
        self.assertAlmostEqual(self.employee.length_of_service, 2.0)

    def test_inital_employment_after_first_contract_date(self):
        # initial employment date is supplied and we have a contract
        # however in this case the initial employment date is after that
        # of the first contract... we expect a exception
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.two_year_ago,
                'date_end': self.one_year_in_future,
                'wage': 5000
            }
        )
        with self.assertRaises(ValidationError):
            self.employee.write({'initial_employment_date': self.one_year_ago})

    def test_length_of_service_at_period_in_history(self):
        # we want to know employee length of service at a point in history
        self.employee.write({'initial_employment_date': self.one_year_ago})
        self.employee = self.employee \
            .with_context(date_now=self.six_months_ago)
        self.assertAlmostEqual(self.employee.length_of_service, 0.5)

    def test_length_of_service_at_period_in_future(self):
        # we want to know how long employee would have worked x months from now
        self.employee.write({'initial_employment_date': self.one_year_ago})
        self.employee = self.employee \
            .with_context(date_now=self.one_year_in_future)
        self.assertAlmostEqual(self.employee.length_of_service, 2.0)

    def test_multiple_contracts_with_no_interval(self):
        # multiple contracts
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.two_year_ago,
                'date_end': self.one_year_ago,
                'wage': 5000
            }
        )
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 2',
                'date_start': self.one_year_ago,
                'date_end': self.now,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 2.0)

    def test_multiple_contracts_with_interval(self):
        # contracts have breaks
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'date_end': self.two_year_ago,
                'wage': 5000
            }
        )
        dt = date.today() - relativedelta(years=1)
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 2',
                'date_start': dt.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_end': self.now,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 2.0)

    def test_duplicate_contracts_1(self):
        # we have duplicate contracts
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'date_end': self.two_year_ago,
                'wage': 5000
            }
        )
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'date_end': self.two_year_ago,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 1.0)

    def test_duplicate_contracts_1(self):
        # we have duplicate contracts
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'wage': 5000
            }
        )
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 3.0)

    def test_overlapping_contracts(self):
        # we have duplicate contracts
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'date_end': self.one_year_ago,
                'wage': 5000
            }
        )
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.two_year_ago,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 3.0)
