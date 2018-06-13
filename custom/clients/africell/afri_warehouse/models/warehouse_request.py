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

    state = fields.Selection([('draft', 'Draft'),
                              ('approval', 'Awaiting Approval'),
                              ('approved', 'Awaiting Delivery'),
                              ('delivered', 'Delivered'),
                              ('confirmed', 'Delivery Confirmed')],
                             default='draft',
                             required=True)

    @api.model
    def _needaction_count(self, domain=None):
        """
         Show a count of draft state reservations on the menu badge.
         """
        return self.search_count([('state', '=', 'approval')])

    @api.multi
    def set_approval(self):
        self.ensure_one()
        for rec in self:
            rec.write({'state': 'approval'})

    @api.multi
    def set_approved(self):
        self.ensure_one()
        for rec in self:
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


