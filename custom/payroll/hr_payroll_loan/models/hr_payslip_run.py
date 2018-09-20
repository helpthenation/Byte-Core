from odoo import api, models
from odoo.exceptions import Warning as UserWarning


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def button_generate_loan_payments(self):
        self.ensure_one()
        if not self.slip_ids:
            raise UserWarning('Please generate payslip before you can '
                              'process loan payments')
        if not self.hr_period_id:
            raise UserWarning('Please specify the Payroll Period')
        employee_ids = self.slip_ids.mapped(lambda r: r.employee_id.id)
        if self.hr_period_id:
            self.env['hr.payroll.loan'].create_payment_amendment(
                self.hr_period_id.id, employee_ids)
            self.slip_ids.compute_sheet()


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        res = super(HrPayslipEmployees, self).compute_sheet()
        run_id = self.env.context['active_id']
        run = self.env['hr.payslip.run'].browse(run_id)
        run.button_generate_loan_payments()
        return res
