from odoo import models, api


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def action_payslips_send(self):
        self.ensure_one()
        self.slip_ids.force_payslip_send()
