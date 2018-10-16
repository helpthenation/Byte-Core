from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class HrHolidaysUpa(models.Model):
    _name = 'hr.holidays.upa'
    _description = "Leave UPA Record"

    holiday_id = fields.Many2one(
        'hr.holidays',
        'Leave',
        required=True,
        ondelete='cascade'
    )
    days = fields.Float(
        required=True
    )
    active_from = fields.Date(
        required=True
    )
    active_to = fields.Date(
        required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        "Employee",
        related='holiday_id.employee_id',
        store=True,
    )
    state = fields.Selection(
        [
            ('draft', 'To Submit'),
            ('cancel', 'Cancelled'),
            ('confirm', 'To Approve'),
            ('refuse', 'Refused'),
            ('validate1', 'Second Approval'),
            ('validate', 'Approved')
        ],
        related='holiday_id.state',
        store=True,
    )

    _sql_constraints = [
        ('unique_holiday_id', 'UNIQUE(holiday_id, active_from)',
         'UPA Leave record must be unique over a period.'),
    ]

    @api.one
    @api.depends('holiday_id')
    def _compute_active_period(self):
        dt = fields.Date.from_string(
            self.holiday_id.date_from) + relativedelta(years=1)
        self.active_from, self.active_to = self.holiday_id.holiday_status_id.ruleset_id.holidays_period(
            self.holiday_id.employee_id, dt)

    @api.model
    def get_outstanding(self, employee_id, dt_str):
        upas = self.search(
            [
                ('employee_id', '=', employee_id),
                ('state', '=', 'validate'),
                ('active_from', '<=', dt_str),
                ('active_to', '>', dt_str)
            ]
        )
        return sum(upas.mapped('days'))
