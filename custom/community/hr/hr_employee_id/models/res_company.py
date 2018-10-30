from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_id_gen_method = fields.Selection(
        selection=[
            ('random', 'Random'),
            ('sequence', 'Sequence'),
        ],
        string="ID Generation Method",
        default='random'
    )
    employee_id_random_digits = fields.Integer(
        string='# of Digits',
        default=5,
        help="Number of digits making up the ID"
    )
    employee_id_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string='Employee ID Sequence',
        help="Pattern to be used for employee ID Generation"
    )
