"""Defining a Payment"""
from odoo import models, fields, api


class AutoPayment(models.Model):
    _name = 'auto.payment'
    _description = 'Service Request Payment Line'
    service_request_id = fields.Many2one(comodel_name='auto.service.request',
                                         string='Service Request',
                                         readonly=True)
    towing_request_id = fields.Many2one(comodel_name='auto.towing.request',
                                        string='Towing Request',
                                        readonly=True)
    payment_mode = fields.Selection([('cash', 'Cash'),
                                     ('electronic', 'Electronic')],
                                    string='Payment Mode',
                                    required=True,
                                    help='Payment mode used')
    amount = fields.Float(string='Amount',
                          required=True,
                          readonly=True,
                          help='Amount Tendered'
                          )
    state = fields.Selection([('draft', 'Draft'),
                              ('paid', 'Paid')],
                             default='draft',
                             readonly=True)
    related_user_id = fields.Many2one(comodel_name='auto.user',
                                      string='User',
                                      required=True,
                                      index=True,
                                      help='User who made payment')
    mechanic_id = fields.Many2one(comodel_name='auto.mechanic',
                                  string='Mechanic',
                                  required=True,
                                  index=True,
                                  help='Driver who made payment')
