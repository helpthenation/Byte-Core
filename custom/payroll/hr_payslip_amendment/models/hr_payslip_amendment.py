# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from odoo import fields, models, api, _
from odoo.exceptions import Warning as UserError


class HrPayslipAmendment(models.Model):
    _name = 'hr.payslip.amendment'
    _description = 'Pay Slip Amendment'
    _inherit = ['mail.thread']

    name = fields.Char(
        'Description',
        size=128,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    hr_period_id = fields.Many2one(
        'hr.period',
        'Payroll Period',
        states={'draft': [('readonly', False)]},
        domain=[('state', '!=', 'done')]
    )
    date = fields.Date(
        'Effective Date',
        readonly=True,
        store=True,
        related='hr_period_id.date_stop'
    )
    category_id = fields.Many2one(
        'hr.payslip.amendment.category',
        'Category',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    input_id = fields.Many2one(
        'hr.rule.input',
        'Salary Rule Input',
        store=True,
        readonly=True,
        related="category_id.input_rule_id"
    )
    slip_id = fields.Many2one(
        'hr.payslip',
        'Paid On',
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    amount = fields.Float(
        'Amount',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="The meaning of this field is dependent on the salary rule "
             "that uses it."
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('validate', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        'State',
        default='draft',
        required=True,
        readonly=True
    )
    note = fields.Text('Memo')

    # _sql_constraints = [
    #     ('duplicate_amendment',
    #      'unique(employee_id, state, hr_period_id, category_id)',
    #      'A similar amendment for this employee has already been created!'),
    # ]

    @api.constrains('employee_id', 'state', 'hr_period_id', 'category_id')
    @api.one
    def _constraint_amendment(self):
        amendment = self.search(
            [
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', self.state),
                ('hr_period_id', '=', self.hr_period_id.id),
                ('category_id', '=', self.category_id.id),
                ('id', '!=', self.id)
            ]
        )
        if amendment:
            raise UserError(
                "Amendment %s (%s) seem to be a duplicate of %s (%s)" % (
                    self.name, self.id, amendment.name, amendment.id))

    @api.onchange('employee_id')
    @api.multi
    def onchange_employee(self):
        self.ensure_one()
        for rec in self:
            if rec.employee_id:
                period = rec.env['hr.period'].get_next_period(
                    rec.env.user.company_id.id,
                    rec.employee_id.contract_id.schedule_pay
                )
                if period:
                    rec.hr_period_id = period.id
                if rec.employee_id.identification_id:
                    rec.name = _('Pay Slip Amendment: %s (%s)') % (
                        rec.employee_id.name,
                        rec.employee_id.identification_id
                    )
                else:
                    rec.name = _('Pay Slip Amendment: %s') % (
                        rec.employee_id.name
                    )

    @api.multi
    def force_unlink(self):
        return self.with_context(force_remove=True).unlink()

    @api.multi
    def unlink(self):
        if not self.env.context.get('force_remove', False):
            for psa in self:
                if psa.state in ['validate', 'done']:
                    raise UserError(
                        'A Pay Slip Amendment that has been confirmed'
                        ' cannot be deleted!')
        return super(HrPayslipAmendment, self).unlink()

    @api.multi
    def action_done(self):
        self.signal_workflow('payslip_done')

    @api.multi
    def action_validate(self):
        self.signal_workflow('validate')

    @api.multi
    def action_reset(self):
        self.write({'state': 'draft'})
        self.create_workflow()
        self.signal_workflow('validate')
        self.write({'slip_id': False})
