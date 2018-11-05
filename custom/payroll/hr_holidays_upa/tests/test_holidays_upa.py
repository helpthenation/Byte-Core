from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHolidaysUpa(common.TransactionCase):

    def setUp(self):
        super(TestHolidaysUpa, self).setUp()
        self.contract_model = self.env["hr.contract"]
        self.employee_model = self.env['hr.employee']
        self.holiday_status_model = self.env['hr.holidays.status']
        self.holiday_model = self.env['hr.holidays']
        self.holiday_upa_model = self.env['hr.holidays.upa']
        self.rule_model = self.env['hr.holidays.evaluation.rule']
        self.ruleset_model = self.env['hr.holidays.evaluation.ruleset']

        self.company = self.env['res.company'].search([], limit=1)
        self.env.user.company_id = self.company.id

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
            'company_id': self.company.id
        })

        # create contract
        self.contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '1990-10-14',
                'wage': 5000,
            }
        )

        # create leave types that we will be manupilating
        self.legal_holiday_type = self.holiday_status_model.create(
            {
                'name': 'Legal Leave',
            }
        )

        # Create fixed ruleset and rules
        self.ruleset_fixed = self.ruleset_model.create({
            'name': 'Ruleset',
            'mode': 'first',
            'period': 'year',
        })
        self.rule_model.create(
            {
                'name': 'Rule',
                'sequence': 1,
                'ruleset_id': self.ruleset_fixed.id,
                'condition_select': 'none',
                'amount': 15
            }
        )
        self.upa_holiday_type = self.holiday_status_model.create(
            {
                'name': 'UPA Leave',
                'ruleset_id': self.ruleset_fixed.id
            }
        )
        self.company.upa_holidays_status_id = self.upa_holiday_type.id
        self.company.upa_first_exhaust_legal = True
        self.sick_holiday_type = self.holiday_status_model.create(
            {
                'name': 'Sick Leave',
                'limit': True,
            }
        )
        self.company.legal_holidays_status_id = self.legal_holiday_type.id

        # let's add out UPA days
        data = {
            'type': 'add',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.upa_holiday_type.id,
            'number_of_days_temp': 15
        }
        holiday = self.holiday_model.create(data)
        holiday.holidays_confirm()
        holiday.holidays_validate()

    def _create_ruleset(self, days=22):
        """ Testing : _create_ruleset """
        ruleset = self.ruleset_model.create({
            'name': 'Ruleset 2',
            'mode': 'first',
            'period': 'year',
        })
        self.rule_model.create(
            {
                'name': 'Rule 2',
                'sequence': 1,
                'ruleset_id': ruleset.id,
                'condition_select': 'none',
                'amount': days
            }
        )
        self.legal_holiday_type.ruleset_id = ruleset.id

    def _take_upa(self, days=10, date_from=None, date_to=None):
        """ Testing : _create_upa """
        data = {
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.upa_holiday_type.id,
            'date_from': date_from or str((date.today() - relativedelta(days=days))),
            'date_to': date_to or str(date.today()),
            'number_of_days_temp': days,
        }
        holiday = self.holiday_model.create(data)
        holiday.holidays_confirm()
        holiday.holidays_validate()
        return holiday

    def test_upa_applicability_1(self):
        """Testing : test_upa_applicability_1"""
        # lets ensure that user can indeed take UPA
        self._create_ruleset()
        with self.assertRaises(ValidationError):
            self._take_upa(days=5)

    def test_upa_applicability_2(self):
        """Testing : test_upa_applicability_2"""
        # lets ensure that user can indeed take UPA
        self._create_ruleset()
        self.company.upa_first_exhaust_legal = False
        self._take_upa(days=5)

    def test_outstanding_deduction_2(self):
        """Testing : test_outstanding_deduction_2"""
        self._create_ruleset()
        self._take_upa()

        # there should be not UPA outstanding for this period
        self.assertEquals(
            self.holiday_upa_model.get_outstanding(self.employee.id,
                                                   str(date.today())), 10
        )

    def test_outstanding_deduction(self):
        """Testing : test_outstanding_deduction"""
        # need to understand this from salton
        self._take_upa()

        # there should be not UPA outstanding for this period
        self.assertEquals(
            self.holiday_upa_model.get_outstanding(self.employee.id,
                                                   str(date.today())), 0
        )

        # but there should be 10 for the next year
        dt = date.today() + relativedelta(years=1)
        self.assertEquals(
            self.holiday_upa_model.get_outstanding(self.employee.id, str(dt)),
            10)

        # we create a ruleset for leave type
        self._create_ruleset()
        employee = self.employee

        # there should be 22 leaves in this since upa calc was done before
        days = self.legal_holiday_type.get_days(employee.id)
        self.assertEqual(days[self.legal_holiday_type.id]['remaining_leaves'],
                         22)

        # there should be only 12 leaves in this since upa
        days = self.legal_holiday_type.get_days(employee.id, dt)
        self.assertEqual(days[self.legal_holiday_type.id]['remaining_leaves'],
                         12)

    def test_outstanding_deduction_2(self):
        """Testing : test_outstanding_deduction_2"""
        employee = self.employee
        self._create_ruleset(days=15)
        data = {
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.legal_holiday_type.id,
            'date_from': str(date(date.today().year, 1, 1)),
            'date_to': str(date(date.today().year, 1, 10)),
            'number_of_days_temp': 10,
        }
        holiday = self.holiday_model.create(data)
        holiday.holidays_confirm()
        holiday.holidays_validate()

        days = self.legal_holiday_type.get_days(employee.id)
        self.assertEqual(days[self.legal_holiday_type.id]['remaining_leaves'],
                         5)

        self._take_upa(days=10,
                       date_from=str(date(date.today().year, 1, 11)),
                       date_to=str(date(date.today().year, 1, 20)))
        days = self.legal_holiday_type.get_days(employee.id)
        self.assertEqual(days[self.legal_holiday_type.id]['remaining_leaves'],
                         0)

        # there should be UPA outstanding for this period
        self.assertEquals(
            self.holiday_upa_model.get_outstanding(self.employee.id,
                                                   str(date.today())), 5
        )

        dt = date.today() + relativedelta(years=1)
        self.assertEquals(
            self.holiday_upa_model.get_outstanding(self.employee.id, str(dt)),
            5)

        days = self.legal_holiday_type.get_days(employee.id, dt=dt)
        self.assertEqual(days[self.legal_holiday_type.id]['remaining_leaves'],
                         10)
