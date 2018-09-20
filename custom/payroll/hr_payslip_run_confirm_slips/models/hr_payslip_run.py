from odoo import models, api
from odoo.exceptions import Warning as UserWarning


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def draft_payslip_run(self):
        self.ensure_one()
        self.slip_ids.reset_amendments()
        self.slip_ids.action_payslip_cancel()
        self.slip_ids.unlink()
        self.write({'state': 'draft'})
        super(HrPayslipRun, self).draft_payslip_run()

    @api.multi
    def close_payslip_run(self):
        self.ensure_one()
        if not self.slip_ids:
            raise UserWarning('You are yet to generate payslips in this run')
        self.slip_ids.action_payslip_done()
        super(HrPayslipRun, self).close_payslip_run()

    @api.multi
    def unlink(self):
        for run in self:
            if run.state != 'draft':
                raise UserWarning(
                    'You need to reset the pay period before you can delete it')
            run.draft_payslip_run()
        super(HrPayslipRun, self).unlink()
