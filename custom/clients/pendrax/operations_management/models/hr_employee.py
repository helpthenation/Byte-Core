# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    zone_id = fields.Many2one(comodel_name='operation.zone', string="Zone")
    is_guard = fields.Boolean(string="Is Guard", default=False)
    available_guard = fields.Boolean(string="Available Guard", default=False, )
    available = fields.Selection([('available', 'Available'),
                                  ('unavailable', 'Unavailable')],
                                 string='Availability',
                                 compute='_compute_guard_state',
                                 default='available')
    guard_type =  fields.Selection([('rover', 'Rover'),
                                    ('standby', 'Standby'),
                                    ('permanent', 'Permanent')])
    current_deployment = fields.Many2one(comodel_name='operation.client', string="Current Deployment")

    @api.depends('available_guard')
    def _compute_guard_state(self):
        for guard in self:
            guard.available = guard.available_guard and 'available' or 'unavailable'

    @api.multi
    @api.depends('is_guard', 'job_id')
    def compute_available_guard(self):
        self.ensure_one()
        for rec in self:
            if rec.is_guard:
                active = False
                assignment_lines = self.env['guards.assignment.line'].search([('guard_id', '=', rec.id)])
                for assignment in assignment_lines:
                    if assignment.status=='active':
                        rec.available_guard = False
                        rec.available = 'unavailable'
                        active = False
                        return
                    if active==False:
                        rec.available_guard=True
                        rec.available ='available'
                        return



