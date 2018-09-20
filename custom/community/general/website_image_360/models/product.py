# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_image_360_ids = fields.One2many('product.image.360', 'product_tmpl_id', string='Images')
    display_360_image = fields.Boolean(string='Display 360 Image')

class ProductImage360(models.Model):
    _name = 'product.image.360'
    _order = 'sequance'	
	
    name = fields.Char(string='Name')
    image = fields.Binary(string='Image', attachment=True)
    product_tmpl_id = fields.Many2one('product.template', string='Related Product', copy=True)
    sequance = fields.Integer(string="Sequance")
