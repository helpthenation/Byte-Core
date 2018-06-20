from odoo import models, fields
import odoo.addons.decimal_precision as dp


class WarehouseRequestLines(models.Model):
    _name = 'warehouse.request.line'
    warehouse_request_id = fields.Many2one(comodel_name='warehouse.request',
                                           required=True,
                                           readonly=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                                   required=True, default=1.0)

