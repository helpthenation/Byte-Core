from odoo import models, fields, api


class EmploymentInactivate(models.TransientModel):
    _name = 'hr.employment.end'
    _description = 'Employee De-Activation Wizard'

    date = fields.Date(
        'Effective Date',
        required=True,
    )
    reason_id = fields.Many2one(
        'hr.employee.termination.reason',
        'Reason',
        required=True
    )
    notes = fields.Text(
        'Notes',
        required=True
    )

    @api.multi
    def apply(self):
        self.ensure_one()
        vals = {
            'name': self.date,
            'employee_id': self.env.context.get('active_id'),
            'reason_id': self.reason_id.id,
            'notes': self.notes,
        }
        self.env['hr.employee.termination'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
