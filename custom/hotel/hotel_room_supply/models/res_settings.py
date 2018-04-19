from odoo import fields, api, models


class HotelSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'hotel.config.settings'
    out_picking_type_id = fields.Many2one('stock.picking.type', string='Out Picking Type')

    @api.model
    def get_default_company_values(self, fields):
        company = self.env.user.company_id
        return {
            'out_picking_type_id': company.out_picking_type_id.id or False
        }

    @api.one
    def set_company_values(self):
        company = self.env.user.company_id
        company.out_picking_type_id = self.out_picking_type_id.id
