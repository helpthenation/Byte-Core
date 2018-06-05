from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    towing_commission = fields.Float(sring='Towing Commission (%)',
                                     default=0.0,
                                     help='Percentage Towing commission that goes to Auto Messiah')
    service_commission = fields.Float(sring='Service Commission (%)',
                                      default=0.0,
                                      help='Percentage Service commission that goes to Auto Messiah')
