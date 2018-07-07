from odoo import models, fields


class HrEmployeeOccupation(models.Model):
    _name = 'hr.children.occupation'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)

