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
from odoo import api, models, fields, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    amendment_count = fields.Integer(
        readony=True,
        compute='_compute_amendment_count'
    )

    @api.multi
    def _compute_amendment_count(self):
        self.ensure_one()
        for rec in self:
            rec.amendment_count = rec.env['hr.payslip.amendment'].search_count(
                [
                    ('slip_id', 'in', rec.slip_ids.ids),
                    ('state', 'in', ('validate', 'draft', 'done'))
                ]
            )

    @api.multi
    def view_run_amendments(self):
        """ Replace the static action used to call the wizard
        """
        self.ensure_one()

        res = {
            'type': 'ir.actions.act_window',
            'name': _('View Amendments'),
            'res_model': 'hr.payslip.amendment',
            'domain': ("[('slip_id','in',%s)]" % (self.slip_ids.ids)),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'target': 'current',
        }

        return res
