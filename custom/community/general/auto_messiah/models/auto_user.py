from odoo import models, fields


class StelmatMechanic(models.Model):
    _inherit = ['ir.needaction_mixin', 'mail.thread', 'res.partner']
    _name = 'auto.user'
    service_request_ids = fields.One2many(comodel_name='auto.service.request',
                                          inverse_name='driver_id',
                                          name='Service Requests')
    towing_request_ids = fields.One2many(comodel_name='auto.towing.request',
                                         inverse_name='driver_id',
                                         name='Towing Requests')
    payment_ids = fields.One2many(comodel_name='auto.payment',
                                  inverse_name='driver_id',
                                  name='Payment History')
    state = fields.Selection([('new', 'New'),
                              ('active', 'Active'),
                              ('suspended', 'Suspended'),
                              ('terminate', 'Terminated'),
                              ('expired', 'Subscription Expired')],
                             string='User Status',
                             required=True)

