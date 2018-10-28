from odoo import models, fields, api

class OperationsZone(models.Model):
    _name = "operation.zone"
    _description = "Zone"
    name = fields.Char(string='Name',
                       required=True,
                       index=True)
    description = fields.Text('Description')
    no_of_guards = fields.Integer('No. of Guards')