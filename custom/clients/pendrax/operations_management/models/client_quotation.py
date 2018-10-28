from odoo import models, fields, api
from datetime import date

class ClientQuotation(models.Model):
    _name = "client.quotation"
    _description = "Client Quotation"
    client_id =  fields.Many2one(comodel_name='operation.client',
                                         required=True,
                                         string="Client",
                                         readonly=True)
    quotation_line_ids = fields.One2many(comodel_name='client.quotation.line',
                                         inverse_name='quotation_id',
                                         string='Quotation Lines')
    date = fields.Date(default=date.today())
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=True)
    ref = fields.Char(string='Reference')
    total = fields.Monetary(compute='_compute_amount', string='Total (Excluding GST)', readonly=True, store=True)
    gst = fields.Monetary(compute='_compute_amount', string='GST Total', readonly=True, store=True)
    grand_total = fields.Monetary(compute='_compute_amount', string='Total (Including GST)', readonly=True, store=True)

    @api.multi
    def get_quote(self):
        return self.env['report'].get_action(self, 'operations_management.client_quote')

    @api.depends('quotation_line_ids.price_subtotal')
    def _compute_amount(self):
        """
        Compute the amounts of the Quotation line.
        """
        total=0.0
        gst=0.0
        for rec in self:
            for line in rec.quotation_line_ids:
                total += line.price_subtotal
                gst += line.price_subtotal*0.15
            rec.update({
                'total': total,
                'gst': gst,
                'grand_total': total+gst,
            })
