from odoo.tests import common


class TestPayslipAmendment(common.TransactionCase):

    def setUp(self):
        super(TestPayslipAmendment, self).setUp()
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

        # Create an employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        # Get structure
        self.structure = self.structure_model.search(
            [('code', '=', 'BASE')])[0]

        # create amendment category and amendment
        self.category1 = self.category_model.create(
            {
                'name': 'Emoloyee Bonus',
                'type': 'add',
                'code': 'BONUSXXX',
                'struct_id': self.structure.id
            }
        )
        self.category2 = self.category_model.create(
            {
                'name': 'Loan Repayment',
                'type': 'subtract',
                'code': 'LOANXXX',
                'struct_id': self.structure.id
            }
        )
        self.category3 = self.category_model.create(
            {
                'name': 'Wrong Category',
                'type': 'subtract',
                'code': 'WRONGXXX',
                'struct_id': self.structure.id
            }
        )
        self.amendment1 = self.amendment_model.create(
            {
                'name': 'Amendment 1',
                'hr_period_id': self.periods[0].id,
                'category_id': self.category1.id,
                'employee_id': self.employee.id,
                'amount': 50000,
            }
        )
        self.amendment1.signal_workflow('validate')
        self.amendment2 = self.amendment_model.create(
            {
                'name': 'Amendment 2',
                'hr_period_id': self.periods[0].id,
                'category_id': self.category2.id,
                'employee_id': self.employee.id,
                'amount': 50000,
            }
        )
        self.amendment2.signal_workflow('validate')
        self.amendment3 = self.amendment_model.create(
            {
                'name': 'Amendment 3',
                'hr_period_id': self.periods[1].id,
                'category_id': self.category3.id,
                'employee_id': self.employee.id,
                'amount': 50000,
            }
        )
        self.amendment3.signal_workflow('validate')
        # Create a contract for the employee
        self.contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'wage': 50000,
                'struct_id': self.structure.id,
                'date_start': '2014-01-01'
            }
        )

        # let's create our payslip
        slip_data = self.payslip_model.onchange_employee_id(
            '2015-01-01', '2015-01-31', self.employee.id, contract_id=False
        )
        res = {
            'employee_id': self.employee.id,
            'name': slip_data['value'].get('name', False),
            'struct_id': slip_data['value'].get('struct_id', False),
            'hr_period_id': self.periods[0].id,
            'contract_id': slip_data['value'].get('contract_id', False),
            'input_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                'input_line_ids', False)],
            'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                'worked_days_line_ids', False)],
            'date_from': '2015-01-01',
            'date_to': '2015-01-31',
        }
        self.slip = self.payslip_model.create(res)
        self.slip.compute_sheet()
        self.slip.action_payslip_done()

    def test_allowance_creation_rule_in_struct(self):
        # tests that the created rule for the amendment is added to the
        # salary structure specified
        self.assertTrue('BONUSXXX' in self.structure.rule_ids.mapped('code'))

    def test_payslip_computation_addition(self):
        # checks that allowance is paid with each pay

        line = self.slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'BONUSXXX')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, 50000.0)  # asset that the correct amount

    def test_payslip_computation_not_added_to_wrong_period(self):
        # checks that allowance is paid with each pay
        line = self.slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'WRONGXXX')
        self.assertEqual(len(line), 0)  # asset that the line is not present

    def test_amendment_state_change(self):
        # checks that allowance is paid with each pay
        self.assertEqual(self.amendment1.state, 'done')

    def test_payslip_computation_deduction(self):
        # checks that allowance is paid at each anniversary
        line = self.slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'LOANXXX')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, -50000.0)  # correct amount
