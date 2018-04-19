
from odoo import models, fields, api


class HotelRoom(models.Model):
    _inherit = 'hotel.room'
    room_supply_ids = fields.One2many('hotel.room.supply', 'room_id',
                                      readonly=True,
                                      string='Room Supplies',
                                      help='Supplier this room has consumed')

