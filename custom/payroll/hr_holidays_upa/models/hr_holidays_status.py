import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    is_upa = fields.Boolean(
        'Is UPA',
        default=False,
        readonly=True,
        compute='_compute_upa_status'
    )

    @api.one
    def _compute_upa_status(self):
        self.is_upa = self == self.env.user.company_id.upa_holidays_status_id
