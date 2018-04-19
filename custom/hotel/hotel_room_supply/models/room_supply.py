from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class RoomSupplyType(models.Model):
    _name = 'hotel.room.supply.type'
    name = fields.Char(string='Name',
                       required=True)
    description = fields.Char(string='Description',
                              help='Describe supply type')

    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'Supply Type must be unique')]


class RoomSupplyLine(models.Model):
    _name = 'hotel.room.supply.line'
    supply_id = fields.Many2one('hotel.room.supply',
                                required=True,
                                readonly=True)
    product_id = fields.Many2one('product.product',
                                 string='Supply',
                                 domain=[('qty_available', '>', 0), ('is_supply', '=', True)],
                                 required=True)
    amount = fields.Integer(string='Quantity',
                            required=True,
                            default=1)


class RoomSupply(models.Model):
    _name = 'hotel.room.supply'
    date = fields.Date(string='Date Supply is made',
                       required=True,
                       readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=datetime.date.today())
    supply_line_ids = fields.One2many('hotel.room.supply.line', 'supply_id',
                                      readonly=True,
                                      states={'draft': [('readonly', False)]},
                                      string='Supplies',
                                      required=True,
                                      help='Add Items to supply room')
    room_id = fields.Many2one('hotel.room',
                              string='Room',
                              required=True,
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              help='Specify room to supply')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('done', 'Done')],
                             default='draft',
                             string='Status',
                             readonly=True)
    supplier_id = fields.Many2one('res.users',
                                  string='Supplied By',
                                  related='create_uid',
                                  readonly=True)
    supply_type_id = fields.Many2one('hotel.room.supply.type',
                                     string='Supply Type',
                                     required=True,
                                     readonly=True,
                                     states={'draft': [('readonly', False)]})

    @api.multi
    def set_confirm(self):
        self.ensure_one()
        for rec in self:
            rec.state = 'confirm'

    @api.multi
    def set_draft(self):
        self.ensure_one()
        for rec in self:
            if not self.room_id and self.supply_line_ids:
                raise ValidationError('Please specify a room and also add supplies')
            rec.state = 'draft'

    @api.multi
    def set_approve(self):
        self.ensure_one()
        for rec in self:
            if rec.supply_line_ids:
                stock_picking_obj = self.env['stock.picking']
                move_obj = self.env['stock.move']
                out_picking_type_id = self.env.user.company_id.out_picking_type_id
                stock_picking = {'min_date': rec.date,
                                 'origin': str('Supply ' + rec.room_id.name + ' ' + str(rec.date)),
                                 'picking_type_id': out_picking_type_id.id,
                                 'location_id': out_picking_type_id.default_location_src_id.id,
                                 'location_dest_id': out_picking_type_id.default_location_dest_id.id}
                stock_picking = stock_picking_obj.create(stock_picking)
                for line in rec.supply_line_ids:
                    qty = line.amount
                    move_line = {'product_id': line.product_id.id,
                                 'name': str('Supply ' + rec.room_id.name + ' ' + str(rec.date)),
                                 'product_uom_qty': qty,
                                 'picking_id': stock_picking.id,
                                 'product_uom': line.product_id.uom_id.id,
                                 'location_id': out_picking_type_id.default_location_src_id.id,
                                 'location_dest_id': out_picking_type_id.default_location_dest_id.id}
                    move_obj.create(move_line)
                    wiz = self.env['stock.immediate.transfer'].create({'pick_id': stock_picking.id})
                    wiz.process()
            rec.state = 'done'
