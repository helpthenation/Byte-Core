from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrPayrollAllowanceLine(models.Model):
    _name = 'hr.payroll.allowance.line'
    _order = "sequence"

    allowance_id = fields.Many2one(
        'hr.payroll.allowance',
        'Allowance',
        required=True,
        ondelete='cascade'
    )
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        related='allowance_id.sequence',
        readonly=True,
        store=True
    )
    code = fields.Char(
        related='allowance_id.code',
        readonly=True,
        store=True
    )
    amount = fields.Float(
        digits=(16, 2),
        required=True
    )
    active = fields.Boolean(
        related='allowance_id.active',
        store=True
    )

    _sql_constraints = [
        (
            'allowance_contract_uniq',
            'unique(allowance_id,contract_id)',
            'You cannot have multiple allowances of the same type on a '
            'contract'
        ),
    ]

    @api.constrains('allowance_id', 'contract_id')
    @api.multi
    def _check_company(self):
        for line in self:
            if (
                len(line.contract_id.employee_id.company_id)
                and len(line.allowance_id.company_id)
                    and line.contract_id.employee_id.company_id.id
                != line.allowance_id.company_id.id
            ):
                raise ValidationError(
                    'Allowance category is not of same company as employee'
                )
        return True
