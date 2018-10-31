from odoo import models,fields


class HrArea(models.Model):
    _name = 'hr.area'
    name = fields.Char(string='Area', required=True)
