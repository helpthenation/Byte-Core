from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'
    department_ids = fields.Many2many(comodel_name='warehouse.department',
                                      rrequired=True,
                                      string='Applicable Departments')
    product_code = fields.Char(string='Part #', copy=False)
    sub_category_code = fields.Char(string='Sub Category Code')


    @api.multi
    def get_parent(self):
        category_object = self.env['product.category']
        all_products = self.search([])
            # Lets get all the categories that are of type category
        for rec in all_products:
            if rec.sub_category_code:
                sub_category = category_object.search([('sub_category_code', '=', rec.sub_category_code)])
                rec.categ_id = sub_category and sub_category.id

        p_category_object = self.env['product.category'].search([('is_category', '=', True)])
        # Lets get all the categories that are of type category
        for rec in p_category_object:
            category = category_object.search([('category_code', '=', rec.category_code)])
            rec.parent_id = category and category.id


