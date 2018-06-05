from odoo import models, fields, api


class AutoSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'auto.settings'
