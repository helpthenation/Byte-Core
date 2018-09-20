
from odoo import models, fields, api


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.employee.config.settings'

    contract_interval = fields.Integer(
        'Interval Between Contract (days)',
        help="Number of days between the end date of a contract and the start "
        "date of a next above which we consider it a break in employee's service length")

    @api.model
    def get_default_contract_interval(self, fields):
        company = self.env.user.company_id
        return {
            'contract_interval': company.contract_interval,
        }

    @api.multi
    def set_contract_interval(self):
        self.ensure_one()
        for rec in self:
            company = rec.env.user.company_id
            company.contract_interval = rec.contract_interval
