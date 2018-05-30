from odoo import fields, models, api
import datetime
from datetime import timedelta


class AutoServiceRequest (models.Model):
    _name = 'auto.service.request'
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
    service_types = fields.Selection([('repair', 'Repair'),
                                      ('maintenance', 'Maintenance'),
                                      ('other', 'Other')],
                                     required=True,
                                     string='Service Type')
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
    description = fields.Html(string='Description',
                              help='Service Description')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [('res_model', '=', self._name)],
                                     auto_join=True, string='Attachments')
    service_reference = fields.Char(string='Service Reference',
                                    readonly=True,
                                    index=True)
    vehicle_model_id = fields.Many2one(comodel_name='auto.vehicle.model',
                                       string='Vehicle Model',
                                       help='Model of the vehicle being repaired')
    issue_reported = fields.Text(string='Issue Reported',
                                 help='Issue Reported by driver')
    issue_diagnosed = fields.Text(string='Issue Diagnosed',
                                  help='Issue Diagnosed by the mechanic')
    state = fields.Selection([('new', 'New'),
                              ('awaiting', 'Awaiting Mechanic'),
                              ('confirm', 'Mechanic Confirmed'),
                              ('started', 'Job Started'),
                              ('finished', 'Job Finished'),
                              ('paid', 'Payment Done')],
                             string="Service Status",
                             readonly=True,
                             default='new')
    payment_line_ids = fields.One2many(comodel_name='auto.payment',
                                       inverse_name='service_request_id',
                                       string='Payment Details',
                                       readonly=True)
    service_amount = fields.Float(string='Service Amount',
                                  required=True,
                                  help='Amount for this service')

