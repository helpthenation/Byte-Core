from odoo import models, fields, api
import datetime


class WarehouseRequest(models.Model):
    _name = 'warehouse.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'reference'
    user_id = fields.Many2one(comodel_name='res.users',
                              default=lambda obj: obj.env.user.id,
                              required=True,
                              index=True)
    department_id = fields.Many2one(comodel_name='warehouse.department',
                                    related='user_id.department_id',
                                    readonly=True,
                                    index=True)
    request_date = fields.Date(string='Request Date',
                               default=datetime.date.today(),
                               required=True)
    delivery_date = fields.Date(string='Delivery Date')
    reference = fields.Char(string='Reference',
                            default=lambda obj: obj.env['ir.sequence'].next_by_code('warehouse.request'),
                            index=True,
                            readonly=True)
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse',
                                   required=True,
                                   string='Warehouse')
    products_line_ids = fields.One2many(comodel_name='warehouse.request.line',
                                        inverse_name='warehouse_request_id',
                                        string='Requests')
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type',
                                      readonly=True,
                                      related='department_id.picking_type_id',
                                      store=True)
    stock_location_id = fields.Many2one(comodel_name='stock.location',
                                        readonly=True,
                                        related='department_id.stock_location_id',
                                        store=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('approval', 'Awaiting Approval'),
                              ('approved', 'Awaiting Delivery'),
                              ('delivered', 'Delivered'),
                              ('confirmed', 'Delivery Confirmed')],
                             default='draft',
                             required=True)
    picking_id = fields.Many2one(comodel_name='stock.picking',
                                 readonly=True)
    '''
    @api.model
    def _needaction_count(self, domain=None):
        """
         Show a count of draft state reservations on the menu badge.
         """
        if self.env.context.get('count_menu') == 'new_warehouse_request':
            return self.search_count([('state', '=', 'approval')])

        if self.env.context.get('count_menu') == 'pending_warehouse_request':
            return self.search_count([('state', '=', 'approved')])

        if self.env.context.get('count_menu') == 'delivered_warehouse_request':
            return self.search_count([('state', '=', 'delivered')])
    '''

    @api.multi
    def set_approval(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'approval'})

    @api.multi
    def set_approved(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        product_lines = []
        for rec in self:
            data = {'picking_type_id': rec.picking_type_id.id,
                    'location_id': rec.warehouse_id.lot_stock_id.id,
                    'location_dest_id': rec.stock_location_id.id,
                    'min_date': rec.request_date}
            for line in rec.products_line_ids:
                product_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'location_id': rec.warehouse_id.lot_stock_id.id,
                            'location_dest_id': rec.stock_location_id.id,
                            'name': 'WHR '+rec.reference,
                            'picking_id': rec.picking_id.id,
                            'product_uom': line.product_id.uom_id.id,
                            'product_uom_qty': line.product_uom_qty}))
            data.update({'move_lines': product_lines})
            picking = picking_obj.create(data)
            rec.picking_id = picking.id
            rec.write({'state': 'approved'})

    @api.multi
    def set_delivered(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'delivered'})

    @api.multi
    def set_confirmed(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'confirmed'})


