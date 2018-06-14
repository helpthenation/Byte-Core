from odoo import models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'
    department_id = fields.Many2one(comodel_name='warehouse.department',
                                    required=True,
                                    string='Related Department')
