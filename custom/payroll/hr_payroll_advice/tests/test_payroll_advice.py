from odoo.tests import common


class TestPayrollAdvice(common.TransactionCase):

    def setUp(self):
        super(TestPayrollAdvice, self).setUp()
        self.payslip_model = self.env["hr.payslip"]
        self.contract_model = self.env["hr.contract"]
        self.rule_model = self.env["hr.salary.rule"]
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.structure_model = self.env["hr.payroll.structure"]
        self.employee_model = self.env['hr.employee']
        #         self.fy_model = self.env['hr.fiscalyear']
        #         self.period_model = self.env['hr.period']
        self.run_model = self.env['hr.payslip.run']
        self.contract_type_model = self.env['hr.contract.type']
        self.bank_model = self.env['res.bank']
        self.partner_bank_model = self.env['res.partner.bank']

        # create contrac type
        type = self.contract_type_model.create(
            {
                'name': 'Normal Employee'
            }
        )

        #         # create pay periods
        #         period_vals = {
        #             'date_start': '2015-01-01',
        #             'date_stop': '2015-12-31',
        #             'schedule_pay': 'monthly',
        #             'payment_day': '2',
        #             'payment_weekday': '0',
        #             'payment_week': '1',
        #             'name': 'Test',
        #         }
        #         fy = self.fy_model.create(period_vals)
        #         fy.create_periods()
        #         fy.button_confirm()
        #         self.periods = fy.period_ids.sorted(key=lambda p: p.date_start)
        #         self.periods[1].button_open()

        # Get structure
        self.structure = self.structure_model.search(
            [('code', '=', 'BASE')])[0]

        self.employees = []
        self.banks = []
        self.bank_accounts = []
        for i in range(10):
            bank = self.bank_model.create({'name': 'Bank ' + str(i)})
            account = self.partner_bank_model.create({
                'acc_number': '123456' + str(i),
                'bank_id': bank.id,
            })
            employee = self.employee_model.create({
                'name': 'Employee ' + str(i),
                'bank_account_id': account.id,
            })
            self.contract_model.create(
                {
                    'employee_id': employee.id,
                    'name': 'Contract ' + str(i),
                    'wage': 500000,
                    'struct_id': self.structure.id,
                    'date_start': '2014-01-01',
                    'type_id': type.id,
                }
            )
            self.employees.append(employee)
            self.banks.append(bank)
            self.bank_accounts.append(account)

        slips = []

        for emp in self.employees:
            slip_data = self.payslip_model.onchange_employee_id(
                '2015-01-01', '2015-01-31', emp.id, contract_id=False
            )
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                    'input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in
                                         slip_data['value'].get(
                                             'worked_days_line_ids', False)],
                'date_from': '2015-01-01',
                'date_to': '2015-01-31',
            }
            slip = self.payslip_model.create(res)
            slip.compute_sheet()
            slips.append(slip.id)
        run = self.run_model.create(
            {
                'name': 'Test',
                'date_start': '2015-01-01',
                'date_end': '2015-01-31',
                'slip_ids': [(6, 0, slips)],
            }
        )

        run.slip_ids.process_sheet()
        self.run = run

    def test_create_advice(self):
        self.run.create_advice()
        self.assertEqual(self.run.advice_count, 10)
        self.assertEqual(self.run.no_advice_employee_count, 0)

    def test_exempted_employees(self):
        for employee in self.employees[:2]:
            employee.bank_account_id = False
        self.run.create_advice()
        self.assertEqual(self.run.no_advice_employee_count, 2)
        self.assertEqual(self.run.advice_count, 8)

    def test_payslip_run_to_draft(self):
        self.run.create_advice()
        self.run.draft_payslip_run()
        self.assertEqual(self.run.advice_count, 0)
        self.assertEqual(self.run.no_advice_employee_count, 0)
