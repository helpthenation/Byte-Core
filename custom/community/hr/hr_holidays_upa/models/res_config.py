from odoo import fields, models, api


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.holidays.config.settings'

    upa_holidays_status_id = fields.Many2one(
        'hr.holidays.status',
        'UPA Leave',
    )
    upa_first_exhaust_legal = fields.Boolean(
        'First Exhaust Legal',
        help="Employee has to first exhaust legal/annual leave before UPA can "
             "be taken"
    )

    @api.model
    def get_default_upa_holidays_status_id(self, fields):
        company = self.env.user.company_id
        return {
            'upa_holidays_status_id': company.upa_holidays_status_id.id,
            'upa_first_exhaust_legal': company.upa_first_exhaust_legal
        }

    @api.one
    def set_upa_holidays_status_id(self):
        company = self.env.user.company_id
        company.upa_holidays_status_id = self.upa_holidays_status_id.id
        company.upa_first_exhaust_legal = self.upa_first_exhaust_legal
