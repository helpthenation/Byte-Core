from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    out_picking_type_id = fields.Many2one('stock.picking.type')
