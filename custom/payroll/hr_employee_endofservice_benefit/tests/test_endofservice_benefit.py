from odoo.tests import common


class TestEndofserviceBenefit(common.TransactionCase):

    def setUp(self):
        super(TestEndofserviceBenefit, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.contract_type_model = self.env['hr.contract.type']
        self.contract_model = self.env['hr.contract']
        self.rule_obj = self.env["hr.salary.rule"]

        # let's create rule
        category = self.env['hr.salary.rule.category'].create(
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
            'amount_python_compute': 'result = 5*1',
            'sequence': 50,
            'condition_python': 'result = True'
        }
        rule = self.rule_obj.create(rule_data)

        type = self.contract_type_model.create(
            {
                'name': 'Normal Employee',
                'benefit_rule_id': rule.id
            }
        )

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
            'initial_employment_date': '2014-01-01'
        })

        # create leave type
        self.contract_model.create(
            {
                'name': 'Contract',
                'wage': 5000,
                'type_id': type.id,
                'employee_id': self.employee.id,
                'state': 'open'
            }
        )

    def test_terminal_benefit(self):
        self.assertEqual(self.employee.terminal_benefit, 5)
