from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'
    department_ids = fields.Many2many(comodel_name='warehouse.department',
                                      rrequired=True,
                                      string='Applicable Departments')
