from odoo import models,fields


class HrContract(models.Model):
    _name = 'hr.contract'

    trial_date_start = fields.Date('Trial Start Date')
    trial_date_end = fields.Date('Trial End Date')