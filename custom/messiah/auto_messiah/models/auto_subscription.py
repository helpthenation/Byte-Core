"""Defining a Subscription"""
from odoo import models, fields, api
import datetime


class AutoPayment(models.Model):
    _name = 'auto.subscription'
    _description = 'Subscription'

    subscription_type_id = fields.Many2one(comodel_name='auto.subscription.type',
                                           string='Subscription Type',
                                           required=True)
    name = fields.Char(string='Subscription', related='subscription_type_id.name')

    related_user_id = fields.Many2one(comodel_name='auto.user',
                                      string='Related User',
                                      required=True)
    start_date = fields.Date(string='Start Date',
                             required=True,
                             help='Subscription Start Date')
    end_date = fields.Date(string='Expiry Date',
                           required=True,
                           help='Subscription Expiry Date')
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired')],
                             default='active',
                             required=True,
                             readonly=True)
    is_current = fields.Boolean(string='Current Subscription',
                                readonly=True,
                                default=False)

    @api.multi
    def set_current_subscription(self):
        self.ensure_one()
        for rec in self:
            for item in self.search(['related_user_id', '=', rec.related_user_id.id]):
                if item.end_date < datetime.date.today():
                    item.is_current = False
        if rec.end_date > datetime.date.today():
            rec.is_current = True
