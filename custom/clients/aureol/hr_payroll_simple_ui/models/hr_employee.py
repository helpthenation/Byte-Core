from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    aureol_staff_category = fields.Selection([('general', 'General staff'),
                                        ('management', 'Management staff')],
                                       string='Staff Categoty',
                                       required=True)