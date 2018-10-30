from odoo import models, fields

class HrOccupation(models.Model):
    _name = 'hr.occupation'
    name = fields.Char(string='Name', required=True)
