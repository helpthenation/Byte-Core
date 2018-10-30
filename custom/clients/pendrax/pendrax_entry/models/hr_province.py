from odoo import models,fields


class HrProvince(models.Model):
    _name = 'hr.province'
    name = fields.Char(string='Name', required=True)
    district_ids = fields.One2many(comodel_name='hr.district', inverse_name='province_id', string='Districts')