# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU AGPL as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from odoo.exceptions import Warning as UserWarning


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    advice_count = fields.Integer(
        compute="_compute_advice_status",
        readonly=True,
        store=True,
    )
    advice_ids = fields.One2many(
        'hr.payroll.advice',
        'batch_id',
        'Bank Advices'
    )
    no_advice_employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string="No Advice",
        _compute='_compute_advice_status',
        store=True,
        readonly=True

    )
    no_advice_employee_count = fields.Integer(
        _compute='_compute_advice_status',
        store=True,
        readonly=True
    )

    @api.depends('advice_ids', 'advice_ids.line_ids')
    def _compute_advice_status(self):

        self.advice_count = len(self.advice_ids)

        # let's get employees not represented here
        adviced_employees = self.advice_ids.mapped('line_ids').mapped(
            'employee_id')
        run_employees = self.slip_ids.mapped('employee_id')
        not_represented = run_employees - adviced_employees

        self.no_advice_employee_ids = [(6, 0, not_represented.ids)]

        self.no_advice_employee_count = len(not_represented.ids)

    @api.multi
    def draft_payslip_run(self):
        res = super(HrPayslipRun, self).draft_payslip_run()
        for run in self:
            run.advice_ids.unlink()
        return res

    @api.multi
    def view_exempted_employees(self):
        """
        view employees not processed by any of the bank advices
        """
        self.ensure_one()

        res = {
            'type': 'ir.actions.act_window',
            'name': 'View Exempted Employees',
            'res_model': 'hr.employee',
            'domain': ("[('id','in',%s)]" % (self.no_advice_employee_ids.ids)),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'target': 'current',
        }

        return res

    @api.multi
    def create_advice(self):
        payslip_pool = self.env['hr.payslip']
        payslip_line_pool = self.env['hr.payslip.line']
        advice_pool = self.env['hr.payroll.advice']
        advice_line_pool = self.env['hr.payroll.advice.line']
        user = self.env.user
        for run in self:
            if run.advice_count:
                raise UserWarning(
                    "Payment advices already exists for %s, 'Set to Draft' to create a new advice." %
                    (run.name))

            # let's get all the banks in this run
            banks = set(
                run.slip_ids.mapped('employee_id.bank_account_id.bank_id'))

            if not banks:
                raise UserWarning('No bank accounts found')

            for bank in banks:
                # let's find the company bank
                company = self.env.user.company_id
                # pay_from = company.bank_ids and company.bank_ids.filtered(lambda r: r.bank_id ==  bank.id) or False

                advice = advice_pool.create({
                    'batch_id': run.id,
                    'company_id': company.id,
                    'name': '%s - %s Advice' % (run.name, bank.name),
                    'date': run.date_end,
                    'bank_id': bank.id,
                    # 'company_bank_id' : pay_from and pay_from[0].id or False
                })
                advice.compute_advice()
