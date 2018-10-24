from odoo import models, fields, api
from datetime import date

class GuardAssignmentLine(models.Model):
    _name = "guards.assignment.line"
    _description = "Guard Assignment"
    related_client_id =  fields.Many2one(comodel_name='operations.client',
                                         required=True,
                                         string="Client",
                                         readonly=True)
    zone = fields.Many2one(comodel_name='operations.zone',
                           string="Zone",
                           related='related_client_id.zone_id',
                           store=True)
    guard_id = fields.Many2one(comodel_name='hr.employee',
                               string="Guard",
                               domain=[('available_guard', '=', True)],
                               required=True)
    status = fields.Selection([('active','Active'),
                               ('inactive', 'Inactive')],
                              default="active",
                              string="Status")
    date_assigned = fields.Date(string='Date Assigned',
                                defult=date.today())