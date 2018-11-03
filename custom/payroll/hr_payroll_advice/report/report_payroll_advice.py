# -*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#    d$
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

from datetime import datetime
from odoo import models, api
from odoo.tools import amount_to_text_en


class payroll_advice_report(models.AbstractModel):
    _name = 'report.hr_payroll_advice.report_payrolladvice'

    def get_month(self, input_date):
        payslip_env = self.env.get('hr.payslip')
        res = {
            'from_name': '', 'to_name': ''
        }
        slip_ids = payslip_env.search([('date_from', '<=', input_date), ('date_to', '>=', input_date)],)
        if slip_ids:
            slip = slip_ids[0]
            from_date = datetime.strptime(slip.date_from, '%Y-%m-%d')
            to_date = datetime.strptime(slip.date_to, '%Y-%m-%d')
            res['from_name'] = from_date.strftime(
                '%d') + '-' + from_date.strftime(
                '%B') + '-' + from_date.strftime(
                '%Y')
            res['to_name'] = to_date.strftime('%d') + '-' + to_date.strftime(
                '%B') + '-' + to_date.strftime('%Y')
        return res

    def convert(self, amount, cur):
        return amount_to_text_en.amount_to_text(amount, 'en', cur)

    def get_bysal_total(self):
        return self.total_bysal

    def get_detail(self, advice):
        result = []
        self.total_bysal = 0.00
        for l in advice.line_ids:
            res = {}
            res.update({
                'name': l.employee_id.name,
                'acc_no': l.name,
                'bysal': l.bysal,
                'debit_credit': l.debit_credit,
            })
            self.total_bysal += l.bysal
            result.append(res)
        return result

    @api.model
    def render_html(self, line_ids, data=None):
        advice = self.env['hr.payroll.advice'].search([('id', '=', line_ids[0])])
        docargs = {
            'doc': advice,
            'data': data,
            'get_month': self.get_month(advice.date),
            'get_detail': self.get_detail(advice),
            'get_bysal_total': self.get_bysal_total(),
            'currency': advice.company_id.currency_id.symbol,
        }
        return self.env['report'].render('hr_payroll_advice.report_payrolladvice', docargs)


