from odoo import models, fields, api
from datetime import date

class GuardAssignmentLine(models.Model):
    _name = "guards.assignment.line"
    _description = "Guard Assignment"
    related_client_id =  fields.Many2one(comodel_name='operation.client',
                                         required=True,
                                         string="Client",
                                         readonly=True)
    zone_id = fields.Many2one(comodel_name='operation.zone',
                           string="Zone",
                           required=True )
    guard_id = fields.Many2one(comodel_name='hr.employee',
                               string="Guard",
                               domain="[('zone_id', '=', zone_id), ('available_guard', '=', True)]",
                               required=True)
    status = fields.Selection([('draft','Draft'),
                               ('active', 'Active'),
                               ('inactive', 'Inactive')],
                              default="draft",
                              string="Status")
    start_date = fields.Date(string='Start Date',
                                default=date.today(),
                             required=True)
    end_date = fields.Date(string='End Date')

    shift = fields.Selection([('day', 'Day'),
                              ('night', 'Night'),
                              ('both', 'Both')],
                             string='Shift',
                             required=True)

    @api.multi
    def confirm_assignment(self):
        self.ensure_one()
        for rec in self:
            rec.write({'status': 'active'})
            rec.guard_id.available_guard=False
            rec.guard_id.available='unavailable'
            rec.guard_id.current_deployment=rec.related_client_id.id
            rec.zone_id.compute_no_of_guards()

    @api.multi
    def unassign(self):
        self.ensure_one()
        for rec in self:
            rec.write({'status': 'inactive'})
            rec.guard_id.available_guard = True
            rec.guard_id.available = 'available'
            rec.guard_id.current_deployment = False
            rec.zone_id.compute_no_of_guards()