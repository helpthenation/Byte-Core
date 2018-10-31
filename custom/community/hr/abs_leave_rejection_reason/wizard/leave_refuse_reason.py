# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source-Today Management Solution
#    Copyright (C) 2018-Today Ascetic Business Solution <www.asceticbs.com>
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
#################################################################################

from odoo import api,fields,models,_

class LeaveRefuseReason(models.TransientModel):
    _name = "leave.refuse.reason"

    leave_refuse_reason = fields.Char(string = "Refuse Reason", required = True)

    def refuse_reason(self):
        if self.env.context.get('active_model') == 'hr.holidays':
            active_model_id = self.env.context.get('active_id')
            hr_obj = self.env['hr.holidays'].search([('id','=',active_model_id)])
            if hr_obj:
                hr_obj.write({'leave_refuse_reason':self.leave_refuse_reason})
                hr_obj.action_refuse()
              
	
