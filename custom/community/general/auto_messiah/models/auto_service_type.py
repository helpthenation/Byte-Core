from odoo import fields, models


class AutoServiceRequestType (models.Model):
    _name = 'auto.service.type'
    name = fields.Char(string='Name',
                       required=True,
                       help='Name of this service type')
    description = fields.Text(string='Description',
                              help='Description of this service type')