from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    remaining_leaves = fields.Integer(
        readonly=True
    )

    @api.one
    @api.depends('initial_employment_date', 'leaves_count',
                 'contract_ids.date_start')
    def _compute_remaining_days(self):
        '''
        we want the cache to invalidate this any of the fields listed as
        dependency is cahnged
        '''
        if isinstance(self.id, models.NewId):
            return

        return super(HrEmployee, self)._compute_remaining_days()
