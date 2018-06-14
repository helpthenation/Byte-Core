from odoo import models,fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    department_id = fields.Many2one(comodel_name='warehouse.department',
                                    string='Department',
                                    )
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse',
                                   string='Warehouse')
