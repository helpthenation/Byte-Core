from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError, Warning as UserWarning
from odoo.tests import common


class TestPayrollLoan(common.TransactionCase):

    def setUp(self):
        super(TestPayrollLoan, self).setUp()
        self.payslip_model = self.env["hr.payslip"]
        self.contract_model = self.env["hr.contract"]
        self.rule_model = self.env["hr.salary.rule"]
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.structure_model = self.env["hr.payroll.structure"]
        self.employee_model = self.env['hr.employee']
        self.category_model = self.env['hr.payslip.amendment.category']
        self.amendment_model = self.env['hr.payslip.amendment']
        self.fy_model = self.env['hr.fiscalyear']
        self.period_model = self.env['hr.period']
        self.loan_model = self.env['hr.payroll.loan']
        self.loan_type_model = self.env['hr.payroll.loan.type']
        self.run_model = self.env['hr.payslip.run']
        self.contract_type_model = self.env['hr.contract.type']
        self.benefit_rule_model = self.env['hr.endofservice.rule']

        # create contrac type
        type = self.contract_type_model.create(
            {
                'name': 'Normal Employee'
            }
        )
        # create terminal rules

        category = self.rule_category_model.create(
            {
                'name': 'benefit',
                'code': 'BEN'
            }
        )
        rule_data = {
            'code': 'benrule',
            'name': 'benefit rule',
            'category_id': category.id,
            'condition_select': 'python',
            'amount_select': 'code',
            'amount_python_compute': 'result = 1000',
            'sequence': 50,
            'condition_python': 'result = True'
        }
        rule = self.rule_model.create(rule_data)

        type = self.contract_type_model.create(
            {
                'name': 'Normal Employee',
                'benefit_rule_id': rule.id
            }
        )

        # create pay periods
        period_vals = {
            'date_start': '2015-01-01',
            'date_stop': '2015-12-31',
            'schedule_pay': 'monthly',
            'payment_day': '2',
            'payment_weekday': '0',
            'payment_week': '1',
            'name': 'Test',
        }
        fy = self.fy_model.create(period_vals)
        fy.create_periods()
        fy.button_confirm()
        self.periods = fy.period_ids.sorted(key=lambda p: p.date_start)
        self.periods[1].button_open()

        # create next period for
        period_vals = {
            'date_start': '2016-01-01',
            'date_stop': '2016-12-31',
            'schedule_pay': 'monthly',
            'payment_day': '2',
            'payment_weekday': '0',
            'payment_week': '1',
            'name': 'Test2',
        }
        fy2 = self.fy_model.create(period_vals)
        fy2.create_periods()
        fy2.button_confirm()

        # Create an employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        self.employee = self.employee.with_context(date_now='2015-01-31')
        # Get structure
        self.structure = self.structure_model.search(
            [('code', '=', 'BASE')])[0]

        # Create a contract for the employee
        self.contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'wage': 500000,
                'struct_id': self.structure.id,
                'date_start': '2014-01-01',
                'type_id': type.id,
                'state': 'open',
            }
        )

    def _make_loan_payment(self, loan, amount, period):
        self.env['hr.payroll.loan.payment'].create({
            'period_id': period.id,
            'loan_id': loan.id,
            'pre_paid': True,
            'amount': amount
        })


    def _create_run(self, date_from='2015-01-01', date_to='2015-01-31',
                    process_sheet=True):
        # let's get the period from dates passed in
        period = self.periods.filtered(
            lambda r: r.date_start == date_from and r.date_stop == date_to)

        # let's create our payslip
        slip_data = self.payslip_model.onchange_employee_id(
            date_from, date_to, self.employee.id, contract_id=False
        )
        res = {
            'employee_id': self.employee.id,
            'name': slip_data['value'].get('name', False),
            'struct_id': slip_data['value'].get('struct_id', False),
            'hr_period_id': period.id,
            'contract_id': slip_data['value'].get('contract_id', False),
            'input_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                'input_line_ids', False)],
            'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                'worked_days_line_ids', False)],
            'date_from': date_from,
            'date_to': date_to,
        }
        slip = self.payslip_model.create(res)
        slip.compute_sheet()
        run = self.run_model.create(
            {
                'name': 'Test',
                'date_start': date_from,
                'date_end': date_to,
                'hr_period_id': period.id,
                'slip_ids': [(4, slip.id)],
                'schedule_pay': 'monthly',
            }
        )
        run.button_generate_loan_payments()
        slip.compute_sheet()
        if process_sheet:
            slip.process_sheet()
        return slip

    def _create_loan_type(self, data=None, code='STAFF'):
        # create loan type
        data = data or {}
        loan_type = self.loan_type_model.create(
            {
                'name': 'Staff Loan',
                'code': code,
                'struct_id': self.structure.id,
                'payment_ratio': data.get('payment_ratio', False),
                'payment_period': data.get('payment_period', 10),
                'condition_select': data.get('condition_select', 'none'),
                'condition_length_min': data.get('condition_length_min', 0),
                'condition_python': data.get(
                    'condition_python',
                    'result = employee.length_of_service >= 1'),
                'interval': data.get('interval', -1),
                'interval_universal': data.get('interval_universal', False),
                'ceiling': data.get('ceiling', 'none'),
                'ceiling_python': data.get(
                    'ceiling_python', 'result = contract.wage'),
                'ceiling_amount': data.get('ceiling_amount', 500000)
            }
        )
        return loan_type

    def _create_loan(self, type_id, data=None, schedule=True, confirm=True):
        data = data or {}
        date_from = data.get('date_from', '2015-01-01')
        dt_default = fields.Date.from_string(date_from) + relativedelta(
            months=10)
        date_to = data.get('date_to', False) and data['date_to'] or str(
            dt_default)
        loan = self.loan_model.create(
            {
                'employee_id': self.employee.id,
                'type_id': type_id,
                'amount': data.get('amount', 500000),
                'installment_amount': data.get('installment_amount', 50000),
                'date_from': date_from,
                'date_to': date_to,

            }
        )
        if confirm:
            loan.button_confirm(schedule=schedule)
        return loan

    def test_simple_loan_creation_ok(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        self.assertTrue(loan)

    def test_loan_date_constrains(self):
        loan_type = self._create_loan_type()
        with self.assertRaises(ValidationError):
            loan = self._create_loan(loan_type.id, {'date_from': '2015-11-01',
                                                    'date_to': '2014-11-01'})

    def test_loan_payment_ratio(self):
        # ensure that we calculate our loan payment ratio well
        ratio = self.loan_model.get_payment_ratio(
            self.employee.id, '2015-01-01', 50000
        )
        self.assertEquals(ratio, 0.1)

        ratio = self.loan_model.get_payment_ratio(
            self.employee.id, '2015-01-01', 100000
        )
        self.assertEquals(ratio, 0.2)

    def test_loan_amount_constrains(self):
        loan_type = self._create_loan_type()
        with self.assertRaises(ValidationError):
            loan = self._create_loan(loan_type.id, {'amount': 0})
        with self.assertRaises(ValidationError):
            loan = self._create_loan(loan_type.id, {'amount': -1000})

    def test_onchange_methods(self):
        loan_type = self._create_loan_type()
        loan = self.loan_model.new({
            'employee_id': self.employee.id,
            'type_id': loan_type.id,
            'amount': 500000,
            'date_from': '2015-01-01',
        })
        loan.onchange_type_id()
        self.assertEquals(loan.date_to, '2015-11-01')
        loan.onchange_date_from()
        self.assertEquals(loan.installment_amount, 50000)

    # def test_loan_deletion(self):
    #     loan_type = self._create_loan_type()
    #     loan = self._create_loan(loan_type.id)
    #     loan.button_confirm()
    #     # let's delete
    #     with self.assertRaises(UserWarning):
    #         loan.unlink()

    def test_button_paid(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        # let's delete
        with self.assertRaises(UserWarning):
            loan.button_paid()

    def test_compute_balance(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        loan.make_payment(periods=self.periods[0])
        self.assertEquals(loan.balance, 450000)
        loan.make_payment(periods=[self.periods[1], self.periods[2]])
        self.assertEquals(loan.balance, 350000)

    def test_loan_amendment_creation(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        self.loan_model.create_payment_amendment(self.periods[0].id,
                                                 [self.employee.id, ])

        self.assertEquals(len(loan.payment_ids.mapped('amendment_id')), 1)
        self.assertEquals(loan.payment_ids.mapped('amendment_id').amount, 50000)

        self.loan_model.create_payment_amendment(self.periods[0].id,
                                                 [self.employee.id, ])
        self.assertEquals(len(loan.payment_ids.mapped('amendment_id')), 1)

        self.loan_model.create_payment_amendment(self.periods[1].id,
                                                 [self.employee.id, ])
        self.assertEquals(len(loan.payment_ids.mapped('amendment_id')), 2)

    def test_payment_negative(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)
        loan.button_confirm()
        with self.assertRaises(ValidationError):
            self._make_loan_payment(loan, amount=-10000, period=self.periods[0])

    def test_payment_above_balance_1(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)
        with self.assertRaises(ValidationError):
            self._make_loan_payment(loan, amount=501000, period=self.periods[0])

    def test_payment_above_balance_2(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)
        self._make_loan_payment(loan, amount=490000, period=self.periods[0])
        with self.assertRaises(ValidationError):
            self._make_loan_payment(loan, amount=100000, period=self.periods[1])

    def test_loan_closing_prepaid(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)
        self._make_loan_payment(loan, amount=500000, period=self.periods[0])
        self.assertEquals(loan.state, 'done')

        loan = self._create_loan(loan_type.id, confirm=False)
        self._make_loan_payment(loan, amount=400000, period=self.periods[0])
        self.assertEquals(loan.state, 'draft')
        self._make_loan_payment(loan, amount=100000, period=self.periods[1])
        self.assertEquals(loan.state, 'done')

    def test_loan_closing_paid(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        loan.make_payment(periods=self.periods[:10])
        self.assertEquals(loan.state, 'done')

    def test_process_payslip(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        self._create_run()
        self.assertEquals(loan.balance, 450000)

    def test_reset_payslip(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        slip = self._create_run()
        slip.cancel_sheet()
        self.assertEquals(loan.balance, 500000)

    def test_condition_select_service_length(self):
        data = {
            'condition_select': 'length',
            'condition_length_min': 1
        }
        loan_type = self._create_loan_type(data)
        loan = self._create_loan(loan_type.id)
        self.assertTrue(loan)

        data = {
            'condition_select': 'length',
            'condition_length_min': 2
        }
        loan_type = self._create_loan_type(data, code='STAFF2')
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type.id)

    def test_condition_select_python(self):
        data = {
            'condition_select': 'python',
            'condition_python': 'result = employee.length_of_service >= 1'
        }
        loan_type = self._create_loan_type(data)
        loan = self._create_loan(loan_type.id)
        self.assertTrue(loan)

        data = {
            'condition_select': 'python',
            'condition_python': 'result = employee.length_of_service >= 2'
        }
        loan_type = self._create_loan_type(data, code='STAFF2')
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type.id)

    def test_intervals_1(self):
        # multiple loans can run
        loan_type = self._create_loan_type({'interval': -1})
        self._create_loan(loan_type.id)
        loan = self._create_loan(loan_type.id)
        self.assertTrue(loan)

    def test_intervals_2_1(self):
        # multiple loan can not run
        loan_type = self._create_loan_type({'interval': 0})
        self._create_loan(loan_type.id)
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type.id)

    def test_intervals_2_2(self):
        # multiple loan can not run
        loan_type = self._create_loan_type({'interval': 0})
        loan = self._create_loan(loan_type.id, confirm=False)  # let's close loan
        self._make_loan_payment(loan, amount=500000, period=self.periods[0])
        loan = self._create_loan(loan_type.id, {'date_from': '2015-10-02'})
        self.assertTrue(loan)

    # def test_intervals_3(self):
    #     # let's add some interval time
    #     loan_type = self._create_loan_type({'interval': 1})
    #     loan = self._create_loan(loan_type.id, confirm=False)
    #     with self.assertRaises(ValidationError):
    #         self._create_loan(loan_type.id)
    #     # let's close loan
    #     self._make_loan_payment(loan, amount=500000, period=self.periods[10])
    #     with self.assertRaises(ValidationError):
    #         self._create_loan(loan_type.id)
    #     with self.assertRaises(ValidationError):
    #         self._create_loan(loan_type.id, {'date_from': '2015-10-14'})
    #     loan = self._create_loan(loan_type.id, {'date_from': '2015-11-01'})
    #     self.assertTrue(loan)

    def test_intervals_universal_1(self):
        loan_type_1 = self._create_loan_type({'interval': 1})
        loan_type_2 = self._create_loan_type({'interval': 1}, code='STAFF2')
        loan = self._create_loan(loan_type_1.id)
        loan1 = self._create_loan(loan_type_2.id)
        self.assertTrue(loan1)

    def test_intervals_universal_2(self):
        loan_type_1 = self._create_loan_type(
            {'interval': 1, 'interval_universal': True})
        loan_type_2 = self._create_loan_type(
            {'interval': 1, 'interval_universal': True}, code='STAFF2')
        loan = self._create_loan(loan_type_1.id)
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type_2.id)

    def test_ceiling_python_under_limit(self):
        loan_type = self._create_loan_type({'ceiling': 'python'})
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        self.assertTrue(loan)

    def test_ceiling_python_over_limit(self):
        loan_type = self._create_loan_type({'ceiling': 'python'})
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type.id, {'amount': 500001})

    def test_ceiling_other_under_limit(self):
        loan_type = self._create_loan_type({'ceiling': 'other'})
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        self.assertTrue(loan)

    def test_ceiling_other_over_limit(self):
        loan_type = self._create_loan_type({'ceiling': 'other'})
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type.id, {'amount': 500001})

    def test_ceiling_benefit_under_limit(self):
        loan_type = self._create_loan_type({'ceiling': 'terminal'})
        loan = self._create_loan(loan_type.id, {'amount': 999})
        loan.button_confirm()
        self.assertTrue(loan)

    def test_ceiling_benefit_over_limit(self):
        loan_type = self._create_loan_type({'ceiling': 'terminal'})
        with self.assertRaises(ValidationError):
            self._create_loan(loan_type.id, {'amount': 1001})

    def test_closed_loan_payment_delete(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)
        self._make_loan_payment(loan, amount=500000, period=self.periods[0])
        self.assertEqual(loan.state, 'done')
        loan.payment_ids.unlink()
        self.assertEqual(loan.state, 'open')

    def test_process_payslip_plan_case_1(self):
        '''
        let's test the first part of the plan case, a possibility that the loan
        might have been closed before we process the new one
        '''
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)
        self._make_loan_payment(loan, amount=450000, period=self.periods[0])
        loan.button_confirm()
        slip1 = self._create_run(process_sheet=False, date_from='2015-02-01',
                                 date_to='2015-02-28')
        self.assertEquals(loan.balance, 50000)

        slip2 = self._create_run(date_from='2015-03-01', date_to='2015-03-31',
                                 process_sheet=False)
        self.assertEquals(loan.balance, 50000)
        line = slip1.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STAFF')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, -50000.0)

        slip1.process_sheet()
        self.assertEquals(loan.balance, 0)

        slip2.process_sheet()
        self.assertEquals(loan.balance, 0)
        line = slip2.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STAFF')
        self.assertEqual(line.total, 0)

    def test_process_payslip_plan_case_2(self):
        '''
        let's test the first part of the plan case, a possibility that the loan
        might have been closed before we process the new one
        '''
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        slip1 = self._create_run(process_sheet=False)
        self.assertEquals(loan.balance, 500000)

        slip2 = self._create_run(date_from='2015-02-01', date_to='2015-02-28',
                                 process_sheet=False)
        self.assertEquals(loan.balance, 500000)
        line = slip2.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STAFF')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, -50000.0)

        slip1.process_sheet()
        self.assertEquals(loan.balance, 450000)

        slip2.process_sheet()
        self.assertEquals(loan.balance, 400000)
        line = slip2.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STAFF')
        self.assertEqual(line.total, -50000.0)

    def test_process_payslip_plan_case_3(self):
        '''
        let's test the first part of the plan case, a possibility that the loan
        might have been closed before we process the new one
        '''
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id, confirm=False)

        self._make_loan_payment(loan, amount=430000, period=self.periods[0])
        loan.button_confirm()
        slip1 = self._create_run(process_sheet=False, date_from='2015-02-01',
                                 date_to='2015-02-28',)
        self.assertEquals(loan.balance, 70000)

        slip2 = self._create_run(date_from='2015-03-01', date_to='2015-03-31',
                                 process_sheet=False)
        self.assertEquals(loan.balance, 70000)
        line = slip1.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STAFF')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, -50000.0)

        slip1.process_sheet()
        self.assertEquals(loan.balance, 20000)

        slip2.process_sheet()
        self.assertEquals(loan.balance, 0)
        line = slip2.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STAFF')
        self.assertTrue(line)  # asset that the line is present
        self.assertEqual(line.total, -20000.0)

    def test_set_balance_1(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        loan.balance = 250000
        self.assertEquals(loan.balance, 250000)

    def test_set_balance_2(self):
        loan_type = self._create_loan_type()
        loan = self._create_loan(loan_type.id)
        loan.button_confirm()
        loan.balance = 50000
        self.assertEquals(loan.balance, 50000)

