from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_id = fields.Many2one(
        store=True,
        readonly=True,
        index=True,
        compute='_compute_current_contract'
    )
    first_contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        store=True,
        readonly=True,
        compute='_compute_first_contract'
    )
    job_id = fields.Many2one(
        readonly=True,
        store=True,
        related='contract_id.job_id'
    )

    @api.one
    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.state',
    )
    def _compute_first_contract(self):
        if self.contract_ids:
            contracts_sorted = self.contract_ids.sorted(
                key=lambda r: (r.date_start, r.id))
            self.first_contract_id = contracts_sorted[0]

    @api.one
    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.date_end',
        'contract_ids.state',
    )
    def _compute_current_contract(self):
        """
        #todo - how do we factor date other than now
        :return:
        """
        # let ensure that we can do things like schedule a contract in the
        # future and be sure that it won't be picked up as the current contract
        contracts = self.contract_ids.filtered(
            lambda r: r.date_start <= fields.Date.today()
            and (not r.date_end or r.date_end >= fields.Date.today())
            and r.state in ('open', 'pending', 'trial_ending')
        )

        if contracts:
            contracts_sorted = contracts.sorted(
                key=lambda r: (r.date_start, r.id))
            self.contract_id = contracts_sorted[-1].id
        else:
            self.contract_id = False

    @api.model
    def try_recomputing_contract(self):
        '''
        contracts whose date_start is set in the future is ignored when current
        contract is being computed so a recomputation is needed when date_start
        = today. To keep this simple and make up for cases in which the server
        might be off we simply recompute for everyone... improvements are
        welcome
        '''
        # TODO implementation has to be improved
        for employee in self.search([]):
            employee._compute_current_contract()
