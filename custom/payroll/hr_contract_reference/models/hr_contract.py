from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    name = fields.Char(
        'Reference',
        required=False,
        readonly=True,
        copy=False,
        default='/'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', False) in ('/', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.ref')
        return super(HrContract, self).create(vals)
