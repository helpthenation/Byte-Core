from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    inactive_ids = fields.One2many(
        'hr.employee.termination',
        'employee_id',
        'Deactivation Records'
    )

    @api.multi
    def end_employment_wizard(self):
        self.ensure_one()

        # let's ensure that we do not currently have a pending termination rec
        # in place; if we do we want to return that
        termination = self.env['hr.employee.termination'].search(
            [
                ('employee_id', '=', self.id),
                ('state', 'in', ('draft', 'confirm'))
            ],
            limit=1,
        )
        if termination:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.termination',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': termination.id
            }
        else:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employment.end',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_employee_id': self.id}
            }

    @api.multi
    def end_employment(self, effective_date=None):
        effective_date = effective_date or fields.Date.today()
        # let's ensure that all open contracts are closed
        contracts = self.env['hr.contract'].search(
            [
                ('employee_id', 'in', self.ids),
                '|',
                ('date_end', '=', False),
                ('date_end', '>', effective_date),
            ]
        )
        contracts.write({'date_end': effective_date, 'state': 'close'})
        self.write({'active': False})

    @api.multi
    def restart_employment(self):
        self.write({'active': True})
