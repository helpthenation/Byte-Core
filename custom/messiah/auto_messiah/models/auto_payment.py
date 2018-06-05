"""Defining a Payment"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime

ERROR_CODES = [{'APS100': 'Amount being paid greater than Total Service Cost'},
               {'APT100': 'Amount being paid greater than Total Towing Cost'}]


class AutoPayment(models.Model):
    _name = 'auto.payment'
    _rec_name = 'payment_reference'
    _description = 'Service Request Payment Line'
    # TODO Pls make all fields like service, towing request, partner etc readonly on production
    service_request_id = fields.Many2one(comodel_name='auto.service',
                                         string='Service Request')
    towing_request_id = fields.Many2one(comodel_name='auto.towing',
                                        string='Towing Request')
    payment_mode = fields.Selection([('cash', 'Cash'),
                                     ('electronic', 'Electronic')],
                                    string='Payment Mode',
                                    required=True,
                                    help='Payment mode used')
    amount = fields.Float(string='Amount',
                          required=True,
                          help='Amount Tendered'
                          )
    state = fields.Selection([('failed', 'Failed'),
                              ('draft', 'Draft'),
                              ('paid', 'Paid')],
                             string="Payment Status",
                             readonly=True,
                             default='draft')
    related_user_id = fields.Many2one(comodel_name='auto.user',
                                      string='User',
                                      compute='compute_user',
                                      store=True,
                                      index=True,
                                      help='User who made payment')
    mechanic_id = fields.Many2one(comodel_name='auto.mechanic',
                                  related='service_request_id.mechanic_id',
                                  string='Mechanic',
                                  index=True,
                                  help='Beneficiary')
    towing_resource_id = fields.Many2one(comodel_name='auto.towing.resource',
                                         related='towing_request_id.towing_resource_id',
                                         string='Towing Resource',
                                         index=True,
                                         help='Driver who made payment')
    payment_reference = fields.Char(string='Payment Reference',
                                    default=lambda obj: obj.env['ir.sequence'].next_by_code('auto.payment'),
                                    readonly=True,
                                    index=True)
    payment_type = fields.Selection([('repair', 'Repair/Maintenance'),
                                     ('towing', 'Towing'),
                                     ('subscription', 'Subscription')],
                                    required=True,
                                    string='Payment for')
    payment_time = fields.Datetime(string='Payment Time',
                                   default=datetime.datetime.now(),
                                   readonly=True)
    auto_messiah_id = fields.Many2one(comodel_name='res.company',
                                      string='Auto Messiah',
                                      defult=1)

    @api.multi
    @api.depends('towing_request_id', 'service_request_id')
    def compute_user(self):
        for rec in self:
            if rec.service_request_id:
                rec.related_user_id = rec.service_request_id.related_user_id.id
            if rec.towing_request_id:
                rec.related_user_id = rec.towing_request_id.related_user_id.id

    @api.multi
    def confirm_payment(self):
        self.ensure_one()
        for payment in self:
            if payment.service_request_id:
                if payment.service_request_id.amount_remain < payment.amount:
                    raise ValidationError('The Total amount being paid should not be greater than the Service Amount'
                                          'Please check existing payments for this service to know '
                                          'how much has already been paid')
                if payment.service_request_id.service_amount >= payment.amount:
                    payment.service_request_id.amount_paid += payment.amount
                payment.write({'state': 'paid'})
            if payment.towing_request_id:
                if payment.towing_request_id.amount_remain < payment.amount:
                    raise ValidationError('The Total amount being paid should not be greater than the Towing Amount'
                                          'Please check existing payments for this towing to know '
                                          'how much has already been paid')
                if payment.towing_request_id.towing_amount >= payment.amount:
                    payment.towing_request_id.amount_paid += payment.amount
                    payment.write({'state': 'paid'})
