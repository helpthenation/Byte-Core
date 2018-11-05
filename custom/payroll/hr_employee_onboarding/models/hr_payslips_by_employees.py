# -*- coding: utf-8 -*-
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

from odoo import models, fields, api
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        employees = self.employee_ids.filtered(
            lambda r: r.status in ('new', 'onboarding'))
        if employees:
            msg = 'The followings employees are still in the "New" or ' \
                  '"Onboarding" state and so can not be included in this pay' \
                  ' batch :" \n'
            for employee in employees:
                msg += 'Employee "%s" (%s) \n' % (
                    employee.name, employee.identification_id
                )
            raise UserError(msg)
        return super(HrPayslipEmployees, self).compute_sheet()
