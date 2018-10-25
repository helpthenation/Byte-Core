from odoo import models, fields
import odoo.addons.decimal_precision as dp


class WarehouseRequestLines(models.Model):
    _name = 'warehouse.request.line'
    category_id = fields.Many2one(comodel_name='product.category',
                                  string='Category',
                                  domain=[('is_category', '=', True)],
                                  required=True)
    sub_category_id = fields.Many2one(comodel_name='product.category', string='Sub Category',
                                      domain="[('parent_id', '=', category_id)]", required=True)
    warehouse_request_id = fields.Many2one(comodel_name='warehouse.request',
                                           required=True,
                                           readonly=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('categ_id', '=', sub_category_id)]",
                                 change_default=True,
                                 ondelete='restrict',
                                 required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                                   required=True, default=1.0)

