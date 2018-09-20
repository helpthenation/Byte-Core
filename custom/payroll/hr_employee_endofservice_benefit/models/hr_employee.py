import math
from datetime import date

from odoo import models, api, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    terminal_benefit = fields.Float(
        'End of Service Benefit',
        readonly=True,
        compute='_compute_employee_terminal_benefit_from_rule'
    )

    @api.one
    @api.depends('initial_employment_date', 'contract_ids',
                 'contract_ids.wage', 'contract_ids.date_start')
    def _compute_employee_terminal_benefit_from_rule(self):
        res = 0
        user = self.env.uid
        self = self.sudo()
        if (not self.contract_id or not self.length_of_service
                or not self.contract_id.type_id.benefit_rule_id):
            self.terminal_benefit = res
            return

        dt = self.env.context.get('date_now', False) or date.today()
        # let's pass this in so that employee service length is computed
        # at our reference date
        employee = self.with_context(date_now=dt)
        localdict = dict(
            employee=employee,
            contract=employee.contract_id,
            job=employee.job_id,
            date_ref=dt,
            result=None,
            math=math
        )

        cr, uid, context = self.env.cr, self.env.uid, self.env.context
        rule_obj = self.pool.get('hr.salary.rule')

        rule_ids = rule_obj._selfursive_search_of_rules(cr, uid, [
            employee.contract_id.type_id.benefit_rule_id, ],
            context=context)
        sorted_rule_ids = [id for id, sequence in
                           sorted(rule_ids, key=lambda x: x[1])]
        for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
            if rule_obj.satisfy_condition(cr, uid, rule.id, localdict,
                                          context=context):
                amount, qty, rate = self.pool['hr.salary.rule'].compute_rule(
                    cr, uid, rule.id, localdict, context=context)
                res = amount * qty
        self = self.sudo(user)
        self.terminal_benefit = res
