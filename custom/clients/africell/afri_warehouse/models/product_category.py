from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _rec_name = 'name'
    is_category = fields.Boolean(string='Top Category', default=False)
