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
from odoo.exceptions import ValidationError, Warning as UserWarning


class PayrollAdvice(models.Model):
    '''
    Bank Advice
    '''
    _name = 'hr.payroll.advice'
    _description = 'Bank Advice'

    name = fields.Char(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/'
    )
    note = fields.Text(
        'Description',
        compute='compute_note',
        store=True
    )
    date = fields.Date(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        help="Advice Date is used to search Payslips",
        default=fields.Date.today
    )
    date_from = fields.Date(
        readonly=True,
        required=True,
    )
    date_to = fields.Date(
        readonly=True,
        required=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('cancel', 'Cancelled'),
        ],
        'Status',
        readonly=True,
        default='draft'
    )
    number = fields.Char(
        'Reference',
        readonly=True
    )
    line_ids = fields.One2many(
        'hr.payroll.advice.line',
        'advice_id',
        'Employee Salary',
        states={'draft': [('readonly', False)]},
        readonly=True,
        copy=True
    )
    cheque_nos = fields.Char('Cheque Numbers')
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='set null',
        default=lambda self: self.env.user.company_id.id
    )
    bank_id = fields.Many2one(
        'res.bank',
        'Bank',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        help="Select the Bank from which the salary is going to be paid"
    )
    company_bank_id = fields.Many2one(
        'res.partner.bank',
        'Pay From Account'
    )
    batch_id = fields.Many2one(
        'hr.payslip.run',
        'Batch',
        required=True
    )
    line_count = fields.Integer(
        compute='_compute_line_count',
        store=True,
        readonly=True
    )

    currency_id = fields.Many2one('res.currency', required=True)

    @api.constrains('company_bank_id')
    def _constrains_company_bank_id(self):
        if self.company_bank_id and self.company_bank_id.bank_id != self.bank_id:
            raise ValidationError(
                'Bank from which payment is being made from cannot be different '
                'from the bank to which advice will be sent')

    @api.depends('line_ids')
    @api.one
    def _compute_line_count(self):
        self.line_count = len(self.line_ids)

    @api.multi
    def compute_note(self):
        gender = ''
        name=''
        account='Account'
        for rec in self:
            if len(rec.line_ids)==1:
                for line in rec.line_ids:
                    if line.employee_id and line.employee_id.gender=='male':
                        gender='his'
                        name = 'name'
                    if line.employee_id and line.employee_id.gender=='female':
                        gender='her'
                        name='name'
            if len(rec.line_ids)>1:
                gender='their'
                name='names'
                account='Accounts'
            # lets get the note
            note = "Upon receipt of this letter, kindly credit the undermentioned " + account +" with the amount against" \
                   " "+ gender +" "+ name + " and Debit our Account Number 01-1031577 with the corresponding amount."
            rec.note=note

    @api.multi
    def compute_advice(self):
        """
        Advice - Create Advice lines in Payment Advice and
        compute Advice lines.
        """
        payslip_pool = self.env['hr.payslip']
        advice_line_pool = self.env['hr.payroll.advice.line']
        payslip_line_pool = self.env['hr.payslip.line']

        for advice in self:
            advice.line_ids.unlink()
            slips = self.batch_id.slip_ids.filtered(
                lambda r: r.state == 'done'
                and r.employee_id.bank_account_id
                and r.employee_id.bank_account_id.bank_id == self.bank_id
            )
            for slip in slips:
                line = payslip_line_pool.search(
                    [('slip_id', '=', slip.id), ('code', '=', 'NET')],
                    limit=1
                )
                if line and line.total>0:
                    advice_line = {
                        'advice_id': advice.id,
                        'account_id': slip.employee_id.bank_account_id.id,
                        'employee_id': slip.employee_id.id,
                        'bysal': line.total,
                        'slip_id': slip.id,
                    }
                    advice_line_pool.create(advice_line)
                    slip.advice_id = advice.id
            advice.compute_note()
        return True

    @api.multi
    def confirm_sheet(self):
        """
        confirm Advice - confirmed Advice after computing Advice Lines..
        """
        seq_obj = self.env['ir.sequence']
        for advice in self:
            if not len(advice.line_ids):
                raise UserWarning(
                    'You can not confirm Payment advice without advice lines.')
            advice_date = fields.Date.from_string(advice.date)
            advice_year = advice_date.strftime(
                '%m') + '-' + advice_date.strftime('%Y')
            number = seq_obj.next_by_code('payment.advice')
            sequence_num = 'PAY' + '/' + advice.bank_id.name + \
                           '/' + advice_year + '/' + number
            self.write({'number': sequence_num, 'state': 'confirm'})
        return True

    @api.multi
    def set_to_draft(self):
        """Resets Advice as draft.
        """
        self.write({'state': 'draft'})

    @api.multi
    def cancel_sheet(self):
        """Marks Advice as cancelled.
        """
        self.write({'state': 'cancel'})
