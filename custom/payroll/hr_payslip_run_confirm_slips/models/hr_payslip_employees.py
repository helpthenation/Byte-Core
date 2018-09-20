from odoo import models, api


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        self.ensure_one()
        run = self.env['hr.payslip.run'].browse(self.env.context['active_id'])
        run_employees = run.slip_ids.mapped('employee_id')
        employees = run_employees & self.employee_ids
        slips = run.slip_ids.filtered(lambda r: r.employee_id in employees)
        slips.unlink()
        super(HrPayslipEmployees, self).compute_sheet()
