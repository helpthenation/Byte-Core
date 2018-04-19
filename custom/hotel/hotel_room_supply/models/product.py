from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.product'
    is_supply = fields.Boolean('Is Supply',
                               default=False,
                               help='Check this button to treat this product as a supply')
