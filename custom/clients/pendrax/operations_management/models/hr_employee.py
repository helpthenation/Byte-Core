# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    zone = fields.Many2one(comodel_name='operations.zone', string="Zone")
    is_guard = fields.Boolean(string="Is Guard", default=False)
    available_guard = fields.Boolean(string="Available Guard", default=False, compute="compute_available_guard", readonly=True)
    guard_type =  fields.Selection([('rover', 'Rover'),
                                    ('standby', 'Standby'),
                                    ('permanent', 'Permanent')])
    current_deployment = fields.Many2one(comodel_name='operations.client', string="Current Deployment")

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
                        active = False
                        return
                    if active==False:
                        rec.available_guard=True
                        return



