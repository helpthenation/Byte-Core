from odoo import fields, models


class HotelRoom(models.Model):
    _inherit = 'hotel.room'
    description = fields.Many2one(string='Description',
                                  related='categ_id.description',
                                  readonly=True)
