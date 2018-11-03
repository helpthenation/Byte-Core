#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import requests


import babel

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def set_to_request(self):
        self.write({'state': 'request'})
        '''
        This function opens a window to compose an email, with email template
        message loaded by default
        '''
        self.ensure_one()

        template = self.env.ref('hr_payroll.email_template_payroll')
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form')
        self = self.with_context(
            default_model='hr.payslip.run',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='mass_mail',
            default_email_from=self.company_id.email,
            mark_so_as_sent=True,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': self.env.context,
        }
