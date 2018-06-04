from odoo import fields, models, api
import datetime
from datetime import timedelta


class AutoService (models.Model):
    _name = 'auto.service'
    _rec_name = 'service_reference'
    mechanic_id = fields.Many2one(comodel_name='auto.mechanic',
                                  string='Assigned Mechanic',
                                  help='Mechanic Assigned to this service',
                                  required=True,
                                  index=True)
    related_user_id = fields.Many2one(comodel_name='auto.user',
                                      help='User related to this job',
                                      string='User',
                                      required=True,
                                      index=True)
    service_type_id = fields.Many2one(comodel_name='auto.service.type',
                                      string='Service Type',
                                      help='Type of Service Done',
                                      required=True)
    service_request_date = fields.Date(string='Service Request Date',
                                       help="Date the service was requested",
                                       required=True,
                                       defailt=datetime.date.today())
    service_start_time = fields.Datetime(string='Service Start Time',
                                         help='Time the service started')
    service_end_time = fields.Datetime(string='Service End Time',
                                       help='Time the service ended')
    service_time = fields.Integer(string="Service Time (Hours)",
                                  help="Time taken to complete the service")
    description = fields.Html(string='Internal Description',
                              help='Service Description')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [('res_model', '=', self._name)],
                                     auto_join=True, string='Attachments')
    service_reference = fields.Char(string='Service Reference',
                                    default=lambda obj: obj.env['ir.sequence'].get('auto.service'),
                                    readonly=True,
                                    index=True)
    vehicle_model_id = fields.Many2one(comodel_name='auto.vehicle.model',
                                       string='Vehicle Model',
                                       help='Model of the vehicle being repaired')
    issue_reported = fields.Text(string='Issue Reported',
                                 help='Issue Reported by driver')
    issue_diagnosed = fields.Text(string='Issue Diagnosed',
                                  help='Issue Diagnosed by the mechanic')
    state = fields.Selection([('cancel', 'Cancelled'),
                              ('awaiting', 'Awaiting Mechanic'),
                              ('confirm', 'Mechanic Confirmed'),
                              ('started', 'Job Started'),
                              ('finished', 'Job Finished'),
                              ('paid', 'Payment Done'),],
                             string="Service Status",
                             readonly=True,
                             default='awaiting')
    payment_ids = fields.One2many(comodel_name='auto.payment',
                                  inverse_name='service_request_id',
                                  string='Payment Details')
    service_amount = fields.Float(string='Service Cost',
                                  required=True,
                                  help='Amount for this service')
    amount_paid = fields.Float(string='Total Paid',
                               help='Total Amount Paid for service',
                               readonly=True)
    amount_remain = fields.Float('Total Balance', compute="_amount_remaining",
                                 store=True, readonly=True)

    @api.multi
    def set_cancel(self):
        for rec in self:
            if rec.mechanic_id and rec.related_user_id:
                rec.write({'state': 'cancel'})

    @api.multi
    def set_awaiting(self):
        for rec in self:
            if rec.mechanic_id and rec.related_user_id:
                rec.write({'state': 'awaiting'})

    @api.multi
    def set_confirm(self):
        for rec in self:
            if rec.mechanic_id and rec.related_user_id:
                rec.write({'state': 'confirm'})

    @api.multi
    def set_start(self):
        for rec in self:
            if rec.mechanic_id and rec.related_user_id:
                rec.write({'state': 'started'})

    @api.multi
    def set_finish(self):
        for rec in self:
            if rec.mechanic_id and rec.related_user_id:
                rec.write({'state': 'finished'})

    @api.multi
    def set_service_paid(self):
        self.ensure_one()
        for service in self:
            if service.mechanic_id and service.related_user_id:
                if service.amount_paid == service.service_amount:
                    service.write({'state': 'paid'})

    @api.multi
    @api.depends('payment_ids.state', 'service_amount')
    def _amount_remaining(self):
        self.ensure_one()
        for service in self:
            service.amount_remain = service.service_amount - service.amount_paid
            service.set_service_paid()
