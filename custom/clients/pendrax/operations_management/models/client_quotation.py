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
    ref = fields.Char(string='Reference',
                      default=lambda obj: obj.env['ir.sequence'].next_by_code('client.quotation'),
                      index=True,
                      readonly=True)
    total = fields.Monetary(compute='_compute_amount', string='Total (Excluding GST)', readonly=True, store=True)
    gst = fields.Monetary(compute='_compute_amount', string='GST Total', readonly=True, store=True)
    grand_total = fields.Monetary(compute='_compute_amount', string='Total (Including GST)', readonly=True, store=True)
    is_acknowledged = fields.Boolean(string='Ok', default=False)

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

    @api.multi
    def folow_up_call(self):
        for rec in self.search([('is_acknowledged','=',False)]):
            email_to=''
            if date.today() > fields.Date.from_string(rec.date):
                operation_users = self.env['res.users'].search(
                    [('groups_id', 'in', (self.env.ref('operations_management.group_operations_officer').id,))])
                if operation_users:
                    subject = "Quotation Follow up reminder for "+str(rec.client_id.name)
                    message = "Helo all, A gentle reminder to follow up on Quotation "\
                              +"with REFERENCE ( "\
                              + str(rec.ref)+ " ) sent to "+str(rec.client_id.name)+" on "+str(rec.date)
                    for user in operation_users:
                        email_to+=user.login+","
                    mail_object = self.env['mail.mail']
                    user = rec.env.user
                    default_email = email_to
                    email = mail_object.create({'subject': subject,
                                                'email_from': user.company_id.email,
                                                'email_to': default_email and default_email,
                                                'body_html': message})
                    email.send()


