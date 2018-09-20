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
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    '''
    Employee Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slips'

    advice_line_ids = fields.One2many(
        'hr.payroll.advice.line',
        'slip_id',
        'Bank Advice Line',
        copy=False,
        readonly=True,
    )

    @api.constrains('advice_line_ids')
    @api.one
    def constrains_advice_line(self):
        # let's ensure that the advice line amount is not more than the net
        # amount on slip
        line = self.filtered(lambda r: r.code == 'NET')
        NET = line.total
        advice_amount = sum(self.advice_line_ids.mapped('bysal'))
        if advice_amount > NET:
            raise ValidationError(
                'Advice amount %s for payslip %s can not be greater than the NET %s' %
                (advice_amount, self.name, NET))
