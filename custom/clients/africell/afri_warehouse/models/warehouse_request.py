from odoo import models, fields, api
import datetime


class WarehouseRequest(models.Model):
    _name = 'warehouse.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'reference'
    user_id = fields.Many2one(comodel_name='res.users',
                              string='Requested By',
                              default=lambda obj: obj.env.user.id,
                              required=True,
                              index=True)
    approved_by_id = fields.Many2one(comodel_name='res.users',
                                     string='Approved by',
                                     index=True)
    receiver_id = fields.Many2one(comodel_name='res.users',
                                  string='Received by',
                                  index=True)
    receiver_name = fields.Char(string='Receiver')
    department_id = fields.Many2one(comodel_name='warehouse.department',
                                    related='user_id.department_id',
                                    store=True,
                                    readonly=True,
                                    index=True)
    reference = fields.Char(string='Reference',
                            default=lambda obj: obj.env['ir.sequence'].next_by_code('warehouse.request'),
                            index=True,
                            readonly=True)
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse',
                                   related='department_id.warehouse_id',
                                   store=True,
                                   string='Warehouse',
                                   readonly=True)
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

    state = fields.Selection([('cancel', 'Cancelled'),
                              ('draft', 'Draft'),
                              ('approval', 'Await Approval'),
                              ('approved', 'Await Availability'),
                              ('availability', 'Available, Await Delivery'),
                              ('delivered', 'Delivered, Await Confirmation'),
                              ('confirmed', 'Delivery Confirmed'),
                              ('receipt', 'Received')],
                             default='draft',
                             required=True)
    picking_id = fields.Many2one(comodel_name='stock.picking',
                                 readonly=True)
    request_date = fields.Date(string='Request Date',
                               default=datetime.date.today(),
                               required=True)
    approval_date = fields.Date(string='Approval Date')
    availability_date = fields.Date(string='Availability Date')
    delivery_date = fields.Date(string='Delivery Date')
    delivery_confirm_date = fields.Date(string='Delivery Confirmed Date')
    receipt_confirm_date = fields.Date(string='Receipt Confirmed Date')

    approval_time = fields.Integer(string='Approval Time (Days)',
                                   readonly=True)
    available_time = fields.Integer(string='Approval Time (Days)',
                                    readonly=True)
    delivery_time = fields.Integer(string='Delivery Time (Days)',
                                   readonly=True)
    delivery_confirm_time = fields.Integer(string='Manager Confirm (Days)',
                                           readonly=True)
    receipt_confirm_time = fields.Integer(string='Receipt Confirm (Days)',
                                          readonly=True)
    operation_time = fields.Integer(string='Entire Operation (Days)',
                                    readonly=True)
    department_note = fields.Text(string='Requester Notes')
    warehouse_note = fields.Text(string='Warehouse Notes')
    procurement_request_id = fields.Many2one(comodel_name='warehouse.procurement.request',
                                             string='Procurement Request',
                                             readonly=True)

    @api.depends('approval_date')
    @api.multi
    def compute_approval_time(self):
        self.ensure_one()
        for rec in self:
            request_date = fields.Datetime.from_string(rec.request_date and rec.request_date).date()
            approval_date = fields.Datetime.from_string(rec.approval_date and rec.approval_date).date()
            rec.approval_time = (approval_date - (request_date and request_date)).days

    @api.depends('availability_date')
    @api.multi
    def available_time(self):
        self.ensure_one()
        for rec in self:
            availability_date = fields.Datetime.from_string(rec.availability_date and rec.availability_date).date()
            approval_date = fields.Datetime.from_string(rec.approval_date and rec.approval_date).date()
            rec.available_time = ((availability_date and availability_date) - (approval_date and approval_date)).days

    @api.depends('delivery_date')
    @api.multi
    def compute_delivery_time(self):
        self.ensure_one()
        for rec in self:
            availability_date = fields.Datetime.from_string(rec.availability_date and rec.availability_date).date()
            delivery_date = fields.Datetime.from_string(rec.delivery_date and rec.delivery_date).date()
            rec.delivery_time = ((delivery_date and delivery_date) - (availability_date and availability_date)).days

    @api.depends('delivery_confirm_date')
    @api.multi
    def compute_delivery_confirm_time(self):
        self.ensure_one()
        for rec in self:
            delivery_confirm_date = fields.Datetime.from_string(rec.delivery_confirm_date and
                                                                rec.delivery_confirm_date).date()
            delivery_date = fields.Datetime.from_string(rec.delivery_date and rec.delivery_date).date()
            rec.delivery_confirm_time = ((delivery_confirm_date and delivery_confirm_date) - (delivery_date and
                                                                                              delivery_date)).days

    @api.depends('receipt_confirm_date')
    @api.multi
    def compute_receipt_time(self):
        self.ensure_one()
        for rec in self:
            delivery_confirm_date = fields.Datetime.from_string(rec.delivery_confirm_date and
                                                                rec.delivery_confirm_date).date() or False
            receipt_confirm_date = fields.Datetime.from_string(rec.receipt_confirm_date and
                                                               rec.receipt_confirm_date).date()
            rec.receipt_confirm_time = ((receipt_confirm_date and receipt_confirm_date) - (delivery_confirm_date and
                                                                                           delivery_confirm_date)).days

    @api.depends('receipt_confirm_date')
    @api.multi
    def compute_operation_time(self):
        self.ensure_one()
        for rec in self:
            request_date = fields.Datetime.from_string(rec.request_date and rec.request_date).date()
            receipt_confirm_date = fields.Datetime.from_string(rec.receipt_confirm_date and
                                                               rec.receipt_confirm_date).date()
            rec.operation_time = ((receipt_confirm_date and receipt_confirm_date) - (request_date and
                                                                                     request_date)).days

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
            rec.write({'state': 'approved',
                       'approval_date': datetime.date.today()})
            if rec.state == 'approved':
                rec.compute_approval_time()
                rec.approved_by_id = self.env.user.id

    @api.multi
    def set_available(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'availability',
                       'availability_date': datetime.date.today()})
            if rec.state == 'availability':
                rec.available_time()

    @api.multi
    def set_delivered(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'delivered',
                       'delivery_date': datetime.date.today()})
            if rec.state == 'delivered':
                rec.compute_delivery_time()

    @api.multi
    def set_delivery_confirmed(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'confirmed',
                       'delivery_confirm_date': datetime.datetime.today()})
            if rec.state == 'confirmed':
                rec.compute_delivery_confirm_time()

    @api.multi
    def set_receipt_confirmed(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'receipt',
                       'receipt_confirm_date': datetime.datetime.today()})
            if rec.state == 'receipt':
                rec.compute_receipt_time()
                rec.compute_operation_time()
                rec.receiver_id = self.env.user.id

    @api.multi
    def set_cancelled(self):
        self.ensure_one()
        for rec in self:
            rec.picking_id.unlink()
            rec.state = 'cancel'

    @api.multi
    def set_reactivate(self):
        self.ensure_one()
        for rec in self:
            rec.state = 'approval'

    @api.multi
    def request_for_products(self):
        self.ensure_one()
        product_lines = []
        for rec in self:
            data = {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'warehouse.procurement.request',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
            for line in rec.products_line_ids:
                product_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty}))
            data.update({'context': {'default_warehouse_request_id': rec.id,
                                     'default_product_request_lines': product_lines}})
        return data

