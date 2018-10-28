from odoo import models, fields, api
from datetime import date

class ClientQuotationLine(models.Model):
    _name = "client.quotation.line"
    _description = "Client Quotation Line"
    quotation_id = fields.Many2one(comodel_name='client.quotation', string='Quotation')
    client_id =  fields.Many2one(comodel_name='operation.client',
                                 related='quotation_id.client_id',
                                 store=True,
                                 string='Client',
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='quotation_id.currency_id')
    guard_type = fields.Selection([('domestic','Domestic  Guards'),
                                   ('commercial', 'Commercial  Guards'),
                                   ('cooperate', 'Cooperate  Guards'),
                                   ('events', 'Events')],
                                  string='Guard Type',
                                  required=True)
    total = fields.Integer(string='Unit')
    cost = fields.Monetary(string='Unit Cost')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    @api.depends('cost', 'total')
    def _compute_amount(self):
        """
        Compute the amounts of the Quotation line.
        """
        for line in self:
            sub_total = line.total*line.cost
            line.update({
                'price_subtotal': sub_total,
            })



