"""Defining a Subscription Type"""
from odoo import models, fields, api
import datetime


class AutoPayment(models.Model):
    _name = 'auto.subscription.type'
    _description = 'Subscription Type'

    name = fields.Char(string='Name',
                       required=True,
                       help='Subscription Type Name')
    description = fields.Char(string='Description',
                              help='Brief Description of this Subscription Type')
