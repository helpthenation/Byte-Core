from odoo import fields, models, api
import datetime
from datetime import timedelta


class AutoServiceRequest (models.Model):
    _name = 'auto.towing.request'
    mechanic_id = fields.Many2one(comodel_name='auto.mechanic',
                                  string='Assigned Towing Partner',
                                  help='Towing Partner Assigned to this job',
                                  required=True,
                                  index=True)
    related_user_id = fields.Many2one(comodel_name='auto.user',
                                      help='User related to this job',
                                      string='User',
                                      required=True,
                                      index=True)
    tow_request_date = fields.Date(string='Tow Request Date',
                                   help="Date the towing was requested",
                                   required=True,
                                   defailt=datetime.date.today())
    towing_start_time = fields.Datetime(string='Towing Start Time',
                                        help='Time the towing job started')
    towing_end_time = fields.Datetime(string='Towing End Time',
                                      help='Time the towing job ended')
    towing_time = fields.Integer(string="Towing Time",
                                 help="Time taken to complete the job")
    towing_distance = fields.Float(string='Towing Distance',
                                   compute='compute_towing_distance',
                                   help='Towing Distance based on start and end point')
    description = fields.Html(string='Description',
                              help='Towing Description')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [('res_model', '=', self._name)],
                                     auto_join=True, string='Attachments')
    towing_reference = fields.Char(string='Towing Reference',
                                   readonly=True,
                                   index=True)
    vehicle_model_id = fields.Many2one(comodel_name='auto.vehicle.model',
                                       string='Vehicle Model',
                                       help='Model of the vehicle being towed')
    state = fields.Selection([('new', 'New'),
                              ('awaiting', 'Awaiting Towing Partner'),
                              ('confirm', 'Towing Partner Confirmed'),
                              ('started', 'Job Started'),
                              ('finished', 'Job Finished'),
                              ('paid', 'Payment Done')],
                             string="Towing Status",
                             readonly=True,
                             default='new')
    payment_line_ids = fields.One2many(comodel_name='auto.payment.line',
                                       inverse_name='tow_request_id',
                                       string='Payment Details',
                                       readonly=True)

