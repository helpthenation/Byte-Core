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

import odoo.addons.decimal_precision as dp

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class PayrollAdviceLine(models.Model):
    '''
    Bank Advice Lines
    '''
    _name = 'hr.payroll.advice.line'
    _description = 'Bank Advice Lines'

    advice_id = fields.Many2one(
        'hr.payroll.advice',
        'Bank Advice',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        'Bank Account No.',
        related='account_id.acc_number',
        store=True,
        readonly=True
    )
    account_id = fields.Many2one(
        'res.partner.bank',
        'Account ID',
        required=True,
        ondelete='cascade'
    )
    slip_id = fields.Many2one(
        'hr.payslip',
        'Payslip',
        required=True,
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True
    )
    bysal = fields.Float(
        'By Salary',
        digits_compute=dp.get_precision('Payroll')
    )
    debit_credit = fields.Selection(
        [('C', 'C'), ('D', 'D')],
        'C/D',
        default='C',
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        readonly=True,
        store=True,
        related='advice_id.company_id'
    )

    @api.constrains('account_id')
    def constrains_account_id(self):
        if self.account_id and self.account_id.bank_id != self.advice_id.bank_id:
            raise ValidationError(
                'Bank of the account of advice line can not be different from the bank of the advice')
