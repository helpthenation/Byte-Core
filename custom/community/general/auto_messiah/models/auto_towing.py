from odoo import fields, models, api
import datetime
from math import sin, cos, sqrt, atan2, radians
from datetime import timedelta


class AutoTowing (models.Model):
    _name = 'auto.towing'
    _rec_name = 'towing_reference'
    towing_resource_id = fields.Many2one(comodel_name='auto.towing.resource',
                                         string='Assigned Towing Partner',
                                         help='Towing Partner Assigned to this job',
                                         required=True,
                                         index=True)
    related_user_id = fields.Many2one(comodel_name='auto.user',
                                      help='User related to this job',
                                      string='User',
                                      required=True,
                                      index=True)
    towing_request_date = fields.Date(string='Tow Request Date',
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
    towing_start_point = fields.Char(string='Towing Start Point',
                                     help='Towing Start Point')
    towing_end_point = fields.Char(string='Towing End Point',
                                   help='Towing End Point')
    description = fields.Html(string='Description',
                              help='Towing Description')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [('res_model', '=', self._name)],
                                     auto_join=True, string='Attachments')
    towing_reference = fields.Char(string='Towing Reference',
                                   default=lambda obj: obj.env['ir.sequence'].next_by_code('auto.towing'),
                                   readonly=True,
                                   index=True)
    vehicle_model_id = fields.Many2one(comodel_name='auto.vehicle.model',
                                       string='Vehicle Model',
                                       help='Model of the vehicle being towed')
    state = fields.Selection([('cancel', 'Cancelled'),
                              ('awaiting', 'Awaiting Towing Partner'),
                              ('confirm', 'Towing Partner Confirmed'),
                              ('started', 'Job Started'),
                              ('finished', 'Job Finished'),
                              ('paid', 'Payment Done')],
                             string="Towing Status",
                             readonly=True,
                             default='new')
    payment_ids = fields.One2many(comodel_name='auto.payment',
                                  inverse_name='towing_request_id',
                                  string='Payment Details')
    towing_amount = fields.Float(string='Towing Cost',
                                 required=True,
                                 help='Amount for this towing')
    amount_paid = fields.Float(string='Total Paid',
                               help='Total Amount Paid for Towing',
                               readonly=True)

    amount_remain = fields.Float('Total Balance', compute="_amount_remaining",
                                 store=True, readonly=True)

    @api.multi
    def set_towing_paid(self):
        self.ensure_one()
        for towing in self:
            if towing.towing_resource_id and towing.related_user_id:
                if towing.amount_paid == towing.towing_amount:
                    towing.write({'state': 'paid'})

    @api.multi
    @api.depends('payment_ids.state', 'towing_amount')
    def _amount_remaining(self):
        self.ensure_one()
        for towing in self:
            towing.amount_remain = towing.towing_amount - towing.amount_paid
            towing.set_towing_paid()

    @api.one
    def compute_distance(self, lt1, lg1, lt2, lg2):
        r = 6373.0

        lat1 = radians(lt1)
        lon1 = radians(lg1)
        lat2 = radians(lt2)
        lon2 = radians(lg2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = r * c
        return distance

    @api.multi
    @api.depends('towing_start_point', 'towing_end_point')
    def compute_towing_distance(self):
        self.ensure_one()
        for rec in self:
            if rec.towing_start_point and rec.towing_end_point:
                rec.towing_distance = rec.compute_distance(rec.towing_start_point[0],
                                                           rec.towing_start_point[1],
                                                           rec.towing_end_point[0],
                                                           rec.towing_end_point[0])
            else:
                rec.towing_distance = 0.0
