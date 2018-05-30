from odoo import models, api, fields


class ResUsers (models.Model):
    _inherit = 'res.users'
    is_mechanic = fields.Boolean(string="Is Mechanic",
                                 default=False,
                                 help='Check if this user is  a mechanic')

    is_driver = fields.Boolean(string="Is Driver",
                               default=False,
                               help='Check if this user is  a Driver')

    is_towing_company = fields.Boolean(string="Is Towing Company",
                                       default=False,
                                       help='Check if this is  a Towing Company')

    is_towing_individual = fields.Boolean(string="Is Towing Individual",
                                          default=False,
                                          help='Check if this is  a Towing Individual')
