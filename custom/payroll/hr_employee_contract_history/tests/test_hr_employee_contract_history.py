from datetime import date, timedelta

from odoo import fields
from odoo.tests import common


class TestEmployeeContractHistory(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeContractHistory, self).setUp()
        self.contract_model = self.env["hr.contract"]
        self.employee_model = self.env['hr.employee']

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        self.contract_1 = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2012-01-01',
                'date_end': '2012-12-31',
                'wage': 5000,
                'state': 'open'
            }
        )
        self.contract_2 = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2013-01-01',
                'wage': 5000,
                'state': 'open'
            }
        )

    def test_next_contract_in_future(self):
        # ad a new contract and see the current contract not updated
        dtEnd = date.today() + timedelta(days=3)
        dtStart = dtEnd + timedelta(days=1)
        self.contract_2.write({'date_end': fields.Date.to_string(dtEnd)})
        contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 3',
                'date_start': fields.Date.to_string(dtStart),
                'wage': 5000,
                'state': 'open'
            }
        )
        self.assertTrue(self.employee.contract_id.id == self.contract_2.id)

    def test_current_contract_ended(self):
        # ad a new contract and see the current contract not updated
        dtEnd = date.today() - timedelta(days=3)
        self.contract_2.write({'date_end': fields.Date.to_string(dtEnd)})
        self.assertFalse(self.employee.contract_id)

    def test_first_contract(self):
        # test first cotract
        self.assertTrue(
            self.employee.first_contract_id.id == self.contract_1.id)

    def test_current_contract(self):
        # test current cotract
        self.assertTrue(self.employee.contract_id.id == self.contract_2.id)

    def test_add_new_first_contract(self):
        # ad a new contract and see the initia contrat reped
        contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2011-01-01',
                'date_end': '2011-12-31',
                'wage': 5000,
                'state': 'open'
            }
        )
        self.assertTrue(
            self.employee.first_contract_id.id == contract.id)

    def test_add_new_current_contract(self):
        # ad a new contract and see the current contract updated
        self.contract_2.write({'date_end': '2013-12-31'})
        contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2014-01-01',
                'date_end': '2100-12-31',
                'wage': 5000,
                'state': 'open'
            }
        )
        self.assertTrue(
            self.employee.contract_id.id == contract.id)
