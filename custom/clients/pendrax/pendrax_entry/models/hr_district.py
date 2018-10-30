from odoo import models,fields


class HrDistrict(models.Model):
    _name = 'hr.district'
    name = fields.Char(string='District', required=True)
    province_id = fields.Many2one(comodel_name='hr.province', string='Province', required=True)
