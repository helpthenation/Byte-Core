# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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

from odoo import models, fields, api
from odoo.exceptions import ValidationError, Warning as UserError


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'ir.needaction_mixin']

    status = fields.Selection(
        [
            ('new', 'New-Hire'),
            ('onboarding', 'On-Boarding'),
            ('active', 'Active'),
            ('pending_inactive', 'Out-Boarding'),
            ('inactive', 'Inactive'),
        ],
        default='new'
    )

    @api.model
    def _needaction_domain_get(self):
        domain = []
        if self.user_has_groups('hr.group_hr_manager'):
            domain = [('status', 'not in', ('active', 'inactive'))]
        return domain

    @api.multi
    def state_active(self):
        self.write({'status': 'active'})

    @api.multi
    def state_pending_inactive(self):
        self.write({'status': 'pending_inactive'})

    @api.multi
    def state_inactive(self):
        self.write({'status': 'inactive'})

    @api.multi
    def state_onboarding(self):
        # lets ensure that all have a contract set
        if self.filtered(lambda r: not r.contract_ids):
            raise UserError(
                'You cannot confirm an employee that does not yet have an employment contract')
        self.write({'status': 'onboarding'})

    @api.multi
    def unlink(self):
        if self.filtered(lambda r: r.status != ('new', 'onboarding')):
            raise ValidationError(
                'You cannot delete an active employee record. '
                'Please inactivate the employee instead!')
        return super(HrEmployee, self).unlink()

    @api.multi
    def restart_employment(self):
        super(HrEmployee, self).restart_employment()
        self.write({'status': 'new'})
