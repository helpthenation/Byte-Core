from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _rec_name = 'name'
    is_category = fields.Boolean(string='Top Category', default=False)
    is_sub_category = fields.Boolean(string='Sub Category', default=False)
    category_code = fields.Char(string='Category Code')
    sub_category_code = fields.Char(string='Sub Category Code')


    @api.multi
    def get_category(self):
        self.ensure_one()
        category_object = self.env['product.category'].search([('is_category', '=', True)])
        sub_category_object = self.env['product.category'].search([('is_sub_category', '=', True)])
        # Lets get all the categories that are of type category
        for rec in sub_category_object:
            category = category_object.search([('category_code', '=', rec.category_code)])
            rec.parent_id = category and category.id

