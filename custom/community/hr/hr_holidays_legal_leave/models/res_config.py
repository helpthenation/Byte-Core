from odoo import fields, models, api


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.holidays.config.settings'

    legal_holidays_status_id = fields.Many2one(
        'hr.holidays.status',
        'Legal Leave',
    )

    @api.model
    def get_default_legal_holidays_status_id(self, fields):
        company = self.env.user.company_id
        return {
            'legal_holidays_status_id': company.legal_holidays_status_id.id,
        }

    @api.one
    def set_legal_holidays_status_id(self):
        company = self.env.user.company_id
        company.legal_holidays_status_id = self.legal_holidays_status_id.id
