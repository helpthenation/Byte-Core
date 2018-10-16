from odoo import models, api


class HrEmployeeTermination(models.Model):
    _inherit = 'hr.employee.termination'

    @api.multi
    def state_cancel(self):
        employees = self.mapped('employee_id')
        employees.state_active()
        return super(HrEmployeeTermination, self).state_cancel()

    @api.multi
    def state_confirm(self):
        employees = self.mapped('employee_id')
        employees.state_pending_inactive()
        return super(HrEmployeeTermination, self).state_confirm()

    @api.multi
    def state_done(self):
        employees = self.mapped('employee_id')
        employees.state_inactive()
        return super(HrEmployeeTermination, self).state_done()
