from odoo import fields, models


class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    benefit_rule_id = fields.Many2one(
        'hr.salary.rule',
        'Terminal Benefit Rule'
    )
