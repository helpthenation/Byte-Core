from odoo import models,fields


class HrQualification(models.Model):
    _name = 'hr.qualification'
    name = fields.Char(string='Name', required=True)

