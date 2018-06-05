from odoo import models, fields, api


class AutoVehicleModel(models.Model):
    _name = 'auto.vehicle.model'
    _description = 'Model of a vehicle'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    brand_id = fields.Many2one('auto.vehicle.brand',
                               string='Make',
                               required=True,
                               help='Make of the vehicle')
    image = fields.Binary(related='brand_id.image', string="Logo")
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)")
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)")

    @api.multi
    @api.depends('name', 'brand_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = record.brand_id.name + '/' + name
            res.append((record.id, name))
        return res

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False
