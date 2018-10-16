from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import Warning as UserError
from odoo.tests import common


class TestEmploymentTermination(common.TransactionCase):

    def setUp(self):
        super(TestEmploymentTermination, self).setUp()
        self.employee_model = self.env['hr.employee']

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        dt = date.today() - relativedelta(months=6)
        self.contract = self.env["hr.contract"].create({
            'name': 'Contract 1',
            'date_start': fields.Date.to_string(dt),
            'employee_id': self.employee.id,
            'wage': 1000,
            'state': 'open',
        })

        # termination
        self.reason = self.env['hr.employee.termination.reason'].create(
            {'name': 'Reason'}
        )
        self.termination = self.env['hr.employee.termination'].create(
            {
                'name': fields.Date.today(),
                'reason_id': self.reason.id,
                'employee_id': self.employee.id,
                'notes': 'Hello World'
            }
        )
        self.termination.state_confirm()

    def test_normal_termination(self):
        self.termination.state_done()
        self.assertEqual(self.employee.active, False)
        self.assertEqual(
            self.contract.date_end, fields.Date.today())

    def test_infuture_contract_end(self):
        dt = date.today() + relativedelta(months=6)
        self.employee.contract_id.date_end = fields.Date.to_string(dt)
        self.termination.state_done()
        self.assertEqual(self.employee.active, False)
        self.assertEqual(
            self.contract.date_end, fields.Date.today())

    def test_cron_termination(self):
        self.env['hr.employee.termination'].try_terminating_ended()
        self.assertEqual(self.employee.active, False)
        self.assertEqual(
            self.contract.date_end, fields.Date.today())

    def test_infuture_effective_dt(self):
        dt = date.today() + relativedelta(months=6)
        self.termination.name = fields.Date.to_string(dt)
        with self.assertRaises(UserError):
            self.termination.state_done()

    def test_termination_exists_wiz(self):
        term = self.employee.end_employment_wizard()
        self.assertEqual(term['res_id'], self.termination.id)
