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
from odoo import api, models, fields


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    amendment_count = fields.Integer(
        readony=True,
        compute='_compute_amendment_count'
    )

    @api.multi
    def _compute_amendment_count(self):
        self.ensure_one()
        for rec in self:
            rec = rec.sudo()
            rec.amendment_count = rec.env['hr.payslip.amendment'].search_count(
                [
                    ('slip_id', '=', rec.id),
                    ('state', 'in', ('validate', 'draft'))
                ]
            )

    @api.multi
    def reset_amendments(self):
        amendments = self.env['hr.payslip.amendment'].search(
            [
                ('slip_id', 'in', self.ids),
                # ('state', '=', 'validate')
            ]
        )
        amendments.action_reset()

    @api.multi
    def compute_sheet(self):
        '''
        let's add amendments
        '''
        for slip in self:
            if slip.hr_period_id:
                for input in slip.input_line_ids:
                    input_rule = self.env['hr.rule.input'].search(
                        [('code', '=', input.code)]
                    )
                    amendments = self.env['hr.payslip.amendment'].search(
                        [
                            ('state', '=', 'validate'),
                            ('hr_period_id', '=', slip.hr_period_id.id),
                            ('employee_id', '=', slip.employee_id.id),
                            ('input_id', '=', input_rule.id),
                            '|',
                            ('slip_id', '=', False),
                            ('slip_id', '=', slip.id),
                        ]
                    )
                    if not amendments:
                        input.amount = 0.0
                    input.amount = sum(amendments.mapped(
                        lambda r: r.category_id.type == 'add'
                        and abs(r.amount) or -(abs(r.amount))))
                    amendments.write({'slip_id': slip.id})
        return super(HrPayslip, self).compute_sheet()

    @api.multi
    def unlink(self):
        self.reset_amendments()
        return super(HrPayslip, self).unlink()

    @api.multi
    def cancel_sheet(self):
        self.reset_amendments()
        return super(HrPayslip, self).action_payslip_cancel()

    @api.one
    def action_payslip_done(self):
        '''
        @todo: check to ensure that input amount is not changed from amendment
               amount
        '''
        super(HrPayslip, self).action_payslip_done()
        amendments = self.env['hr.payslip.amendment'].search(
            [
                ('slip_id', '=', self.id),
                ('state', '=', 'validate')
            ]
        )
        amendments.action_done()
