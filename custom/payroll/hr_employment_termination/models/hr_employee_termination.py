
from odoo import fields, models, api
from odoo.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)


class HrEmployeeTermination(models.Model):
    _name = 'hr.employee.termination'
    _description = 'Data Related to Deactivation of Employee'
    _order = "id DESC"

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Date(
        'Effective Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    display_name = fields.Char(
        _compute='_compute_description',
        store=True
    )
    reason_id = fields.Many2one(
        'hr.employee.termination.reason',
        'Reason',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    notes = fields.Text(
        'Notes',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True
    )
    department_id = fields.Many2one(
        'hr.department',
        "Department",
        store=True,
        readonly=True,
        related='employee_id.department_id'
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        readonly=True,
        default='draft',
        track_visibility='onchange'
    )

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(HrEmployeeTermination, self).create(vals)
        if res.employee_id.parent_id and res.employee_id.parent_id.user_id:
            res.message_subscribe_users(
                user_ids=[res.employee_id.parent_id.user_id.id])
        if (
            res.employee_id.department_id.manager_id and res.employee_id.department_id.manager_id.user_id
            and res.employee_id.parent_id
                and res.employee_id.department_id.manager_id != res.employee_id.parent_id):
            res.message_subscribe_users(
                user_ids=[res.employee_id.department_id.manager_id.user_id.id])

        # let's subscribe hr_users
        hr_users = self.env['res.users'].search(
            [('groups_id', 'in', (self.env.ref('hr.group_hr_user').id,))])
        if hr_users:
            res.message_subscribe_users(user_ids=hr_users.ids)

        # let's send an email notifying people about this
        try:
            mail_template = self.env.ref(
                'hr_employment_termination.termination_email')
            if mail_template:
                mail_template.send_mail(res.id)
        except Exception as e:
            _logger.exception()
        return res

    @api.one
    @api.depends('employee_id')
    def _compute_description(self):
        if self.employee_id:
            self.description = 'Termination Workflow started for %s' % self.employee_id.name

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.display_name))
        return result

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        domain = []

        if users_obj.has_group('hr.group_hr_user'):
            domain = [('state', 'in', ['draft'])]

        if users_obj.has_group('hr.group_hr_manager'):
            if len(domain) > 0:
                domain = ['|'] + domain + [('state', '=', 'confirm')]
            else:
                domain = [('state', '=', 'confirm')]

        return domain

    @api.multi
    def unlink(self):
        res = self.filtered(lambda r: r.state != 'draft')
        if res:
            raise UserError('Employment termination already in progress. '
                            'Use the "Cancel" button instead.')

        return super(HrEmployeeTermination, self).unlink()

    @api.multi
    def state_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def state_confirm(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def state_done(self):
        today = fields.Date.today()
        for termination in self:
            if today < termination.name:
                raise UserError('Unable to deactivate employee, effective '
                                'date is still in the future!')
            termination.employee_id.end_employment(termination.name)

        return self.write({'state': 'done'})

    @api.model
    def try_terminating_ended(self):
        self.search(
            [('state', '=', 'confirm'),
             ('name', '<=', fields.Date.today())]
        ).state_done()
