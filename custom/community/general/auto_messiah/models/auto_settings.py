from odoo import models, fields, api


class AutoSettings(models.TransientModel):
    _inherit = 'auto.settings'
    towing_commission = fields.Float(sring='Towing Commission (%)',
                                     default=0.0,
                                     help='Percentage Towing commission that goes to Auto Messiah')
    service_commission = fields.Float(sring='Service Commission (%)',
                                      default=0.0,
                                      help='Percentage Service commission that goes to Auto Messiah')

    @api.model
    def get_default_company_values(self, fields):
        company = self.env.user.company_id
        return {
            'towing_commission': company.towing_commission,
            'service_commission': company.service_commission
        }

    @api.one
    def set_company_values(self):
        company = self.env.user.company_id
        company.towing_commission = self.towing_commission
        company.service_commission = self.service_commission
