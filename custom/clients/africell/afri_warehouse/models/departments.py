from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RequestDepartment(models.Model):
    _name = 'warehouse.department'
    name = fields.Char(string='Department Name',
                       required=True,
                       index=True)
    manager_id = fields.Many2one(comodel_name='res.users',
                                 required=True)
    description = fields.Text(string='Description')
    stock_location_id = fields.Many2one(comodel_name='stock.location',
                                        string='Consumption Location',
                                        required=True)

    @api.constrains
    @api.depends('stock_location_id')
    def check_stock_location(self):
        if self.stock_location_id and self.stock_location_id.usage != 'customer':
            raise ValidationError('Invalid location Please. Please select a location of usage type customer')
