from odoo import models, fields


class HrEndofserviceRule(models.Model):
    _name = 'hr.endofservice.rule'
    _rec_name = 'days'

    contract_type_id = fields.Many2one(
        'hr.contract.type',
        'Contract Type',
        requried=True
    )
    range_from = fields.Integer(
        required=True,
        help="Service length range start in years"
    )
    range_to = fields.Integer(
        required=True,
        help="Service length range end in years"
    )
    days = fields.Integer(
        'Working Days Pay',
        required=True,
        help="Amount of working days to pay"
    )
