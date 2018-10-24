# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Job(models.Model):
    _inherit = "hr.job"
    guard_position = fields.Boolean(default=False, string="Guard Position")