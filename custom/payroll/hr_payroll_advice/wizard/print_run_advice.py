# -*- coding:utf-8 -*-
from odoo import models, api
from odoo.exceptions import Warning


class print_run_advice(models.TransientModel):
    _name = 'print.run.advice'
    _description = 'Print Advice'

    @api.multi
    def print_advice(self):
        self.ensure_one()
        run_id = self.env.context['active_id']
        run = self.env['hr.payslip.run'].browse(run_id)
        if not run.advice_count:
            raise Warning('You must first create an advice before you can '
                          'print one')

        advices = run.advice_ids.filtered(lambda r: r.state == 'confirm')
        datas = {
            'model': 'hr.payroll.advice',
            'ids': advices.ids,
        }
        report_obj = self.env['report'].with_context(
            active_ids=advices.ids,
            active_model='hr.payroll.advice'
        )
        return report_obj.get_action(
            advices,
            'hr_payroll_advice.report_payrolladvice',
            data=datas
        )
