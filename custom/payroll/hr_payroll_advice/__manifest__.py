# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
{
    'name': 'Payroll Advice',
    'category': 'Human Resources',
    'author': 'Francis Bangura<fbangura@byteltd.com>',
    'license': 'AGPL-3',
    'website': 'http://byteltd.com',
    'depends': ['hr_payroll', 'hr_payslip_run_button_box'],
    'version': '1.0',
    'description': """
Payroll Advice
==============

    - Payroll Advice and Report
    """,
    'data': [
        #'security/ir.model.access.csv',
        'hr_payroll_advice_report.xml',
        'data/hr_payroll_advice_sequence.xml',
        'views/report_payrolladvice.xml',
        'wizard/print_run_advice_view.xml',
        'views/hr_payroll_advice.xml',
        'views/hr_payslip_run.xml',
        'views/hr_payslip.xml',
        'views/hr_payroll_advice_line.xml',
        'views/report_payslip.xml',
        'views/report_payslipdetails.xml',

    ],
    'installable': True
}
