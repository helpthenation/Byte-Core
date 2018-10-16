import calendar
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning as UserError
from odoo.tools.float_utils import float_is_zero
from odoo import SUPERUSER_ID


class HrPayrollLoan(models.Model):
    _name = 'hr.payroll.loan'
    _order = 'date_from DESC'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(
        'Reference',
        readonly=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    type_id = fields.Many2one(
        'hr.payroll.loan.type',
        'Loan Type',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    amount = fields.Float(
        'Amount',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    installment_amount = fields.Float(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    interest_rate = fields.Float(
        'Interest Rate',
        readonly=True,
        default=0.0,
        states={'draft': [('readonly', False)]}
    )
    date_from = fields.Date(
        'Loan Period Start',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    date_to = fields.Date(
        'Loan Period End',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_closed = fields.Date(
        'Closed On',
        readonly=True
    )
    balance = fields.Float(
        store=True,
        compute="_compute_balance",
    )
    payment_ids = fields.One2many(
        'hr.payroll.loan.payment',
        'loan_id',
        'Payments',
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('open', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        default='draft',
    )
    note = fields.Text()

    @api.multi
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        self.ensure_one()
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError('End date cannot be before start date')
            return True

    @api.model
    def get_payment_ratio(self, employee_id, date_str, installment_amount):
        # let's calculate the employee's net
        slip_pool = self.env['hr.payslip']
        # let's have from and to date compounding our loan start date
        dt_start = fields.Date.from_string(date_str)
        last_day_in_month = calendar.monthrange(
            dt_start.year, dt_start.month)[1]
        from_date = fields.Date.to_string(
            date(dt_start.year, dt_start.month, 1))
        to_date = fields.Date.to_string(
            date(dt_start.year, dt_start.month, last_day_in_month))

        slip_data = slip_pool.onchange_employee_id(
            from_date, to_date, employee_id, contract_id=False)
        res = {
            'employee_id': employee_id,
            'name': slip_data['value'].get('name', False),
            'struct_id': slip_data['value'].get('struct_id', False),
            'contract_id': slip_data['value'].get('contract_id', False),
            'input_line_ids': [(0, 0, x) for x in
                               slip_data['value'].get('input_line_ids', False)],
            'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                'worked_days_line_ids', False)],
            'date_from': from_date,
            'date_to': to_date,
        }
        net_amount = 0.0
        # let's run in new env so that we can rollback easily
        cr = self.env.cr
        cr.execute('SAVEPOINT dry_run_slip')
        slip = slip_pool.create(res)
        slip.compute_sheet()
        net = slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'NET')
        if not net:
            raise UserError('Cannot find the rule with the code NET')
        net_amount = net.total
        cr.execute('ROLLBACK TO SAVEPOINT dry_run_slip')

        return net_amount and installment_amount / float(net_amount) or 0

    @api.constrains('payment_ids')
    @api.multi
    def _constraint_payment_amount(self):
        self.ensure_one()
        for rec in self:
            amount = sum(rec.payment_ids.mapped('amount'))
            precision = rec.env['decimal.precision'].precision_get('Payroll')
            if rec.state != 'draft' and float_compare(
                    rec.amount, amount, precision_digits=precision) != 0:
                raise ValidationError(
                    'Total payment schedule %s has to be equal to loan amount %s '
                    'for loan %s' % (amount, rec.amount, rec.name))

    @api.multi
    @api.constrains('amount')
    def _amount_nonzero(self):
        self.ensure_one()
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(
                    'Requested amount can not be zero or negative')
            return True

    @api.multi
    @api.depends('payment_ids', 'amount', 'payment_ids.amount',
                 'payment_ids.paid')
    def _compute_balance(self):
        self.ensure_one()
        for rec in self:
            if rec.amount == 0:
                return 0
            balance = sum(
                rec.payment_ids.filtered(
                    lambda r: r.paid).mapped('amount')
            )
            if balance < 0:
                raise ValidationError(
                    'Loan %s balance is being computed as negative' % rec.name)
            rec.balance = rec.amount - balance

    @api.multi
    @api.onchange('date_from', 'date_to', 'amount')
    def onchange_date_from(self):
        self.ensure_one()
        for rec in self:
            if rec.date_from and rec.date_to:
                d2 = fields.Date.from_string(rec.date_from)
                d1 = fields.Date.from_string(rec.date_to)
                months = (d1.year - d2.year) * 12 + d1.month - d2.month
                if months >= 1:
                    rec.installment_amount = rec.amount / months

    @api.multi
    @api.onchange('date_from', 'type_id')
    def onchange_type_id(self):
        self.ensure_one()
        for rec in self:
            if rec.type_id and rec.date_from:
                date_from = fields.Date.from_string(rec.date_from)
                date_to = date_from + relativedelta(
                    months=rec.type_id.payment_period)
                rec.date_to = fields.Date.to_string(date_to)

    @api.model
    def create(self, data):
        employee = self.env['hr.employee'].browse(data['employee_id'])
        dt = fields.Date.from_string(data['date_from'])
        type = self.env['hr.payroll.loan.type'].browse(data['type_id'])
        employee = employee.with_context(date_now=dt)
        localdict = dict(
            employee=employee,
            contract=employee.contract_id,
            job=employee.job_id,
            date_ref=dt,
            result=None,
        )

        if not employee.contract_id.struct_id:
            raise UserError('Employee does not have a salary structure!')
        # let's ensure that user qualifies for loan
        if not type.satisfy_condition(localdict):
            raise ValidationError('Employee does not qualify for this '
                                  'loan type!')

        # let's ensure that interval is past
        if not type.check_interval_since_last(data['date_from'],
                                              data['employee_id']):
            raise ValidationError(
                'Required interval between loans not reached!')

        # let's check to ensure that loan is less than ceiling
        if not type.check_ceiling(data['amount'], localdict):
            raise ValidationError('Amount requested is greater than what '
                                  'employee qualifies for this loan type!')

        # let's ensure that user will not be going past the  payment ratio
        if type.payment_ratio > 0:
            ratio = self.get_payment_ratio(
                data['employee_id'], data['date_from'],
                data['installment_amount']
            )
            if ratio > type.payment_ratio:
                raise ValidationError(
                    'Ratio of salary to payment is greater than '
                    'allowed for this loan type')

        data['name'] = self.env['ir.sequence'].next_by_code('payroll.loan.ref')
        return super(HrPayrollLoan, self).create(data)

    @api.multi
    def copy(self):
        """ stop users from making copies
        """
        raise UserError('Loans does not support duplication!')

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state != 'draft' and not self.env.user.id == SUPERUSER_ID:
                raise UserError(
                    'Cannot delete loan requests not in the draft '
                    'state.')
        return super(HrPayrollLoan, self).unlink()

    @api.multi
    def generate_payment_schedule(self):
        """
        generates payment schedule
        :return:
        """
        self.ensure_one()
        payments = self.payment_ids.filtered(lambda r: not r.paid)
        payments.unlink()
        principal = self.balance
        period_obj = self.env['hr.period']

        existing_periods = self.payment_ids.filtered(
            lambda r: r.paid).mapped('period_id')
        period = period_obj.get_period_from_date(
            company_id=self.employee_id.company_id.id,
            date_str=self.date_from
        )
        if not period:
            raise ValidationError(
                'Defined pay periods do not cover the entire period of %s '
                'to %s of the loan %s' % (
                    self.date_from, self.date_to, self.name))
        while principal > 0:
            if period not in existing_periods:
                payment_amount = (principal > self.installment_amount
                                  and self.installment_amount or principal)
                self.schedule_payment(amount=payment_amount, period=period)
                principal -= payment_amount
            try:
                period = period.get_next()
            except IndexError:
                raise ValidationError(
                    'Defined pay periods do not cover the entire period of %s '
                    'to %s of the loan %s' % (
                        self.date_from, self.date_to, self.name))
            if not period:
                raise ValidationError(
                    'Defined pay periods do not cover the entire period of %s '
                    'to %s of the loan %s' % (
                        self.date_from, self.date_to, self.name))

    @api.multi
    def button_confirm(self, schedule=True):
        self.ensure_one()
        if sum(self.payment_ids.mapped('amount')) < self.amount and schedule:
            self.generate_payment_schedule()

        if not self.payment_ids:
            raise ValidationError('Please generate payment schedule')

        amount = sum(self.payment_ids.mapped('amount'))
        precision = self.env['decimal.precision'].precision_get('Payroll')

        if not float_is_zero(abs(amount - self.amount),
                             precision_digits=precision):
            raise ValidationError('Scheduled payment amount %s has to be equal '
                                  'to the loan amount %s' % (
                                        amount, self.amount))

        self.write({'state': 'open'})

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def button_view_paid(self):
        # view is sending in context in place of dt in button_paid so this is
        # meant to fix that
        self.button_paid()

    @api.multi
    def button_reset(self):
        self.write({'state': 'draft'})

    @api.multi
    def button_paid(self, dt=None):
        dt = dt or fields.Date.today()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        if self.filtered(lambda r: not float_is_zero(
                r.balance, precision_digits=precision)):
            raise UserError('Cannot close open loans with a running balance')
        return self.write({'state': 'done',
                           'date_closed': dt})

    @api.multi
    def schedule_payment(self, amount, period):
        '''
        makes payment against a loan
        '''
        self.ensure_one()
        for rec in self:
            payment_data = {
                'loan_id': rec.id,
                'amount': amount,
                'period_id': period.id,
            }
            rec.env['hr.payroll.loan.payment'].create(payment_data)

    @api.multi
    def make_payment(self, amount=None, periods=None, amendment_id=None, dt=None):
        '''
        makes payment against a loan
        '''
        self.ensure_one()
        for rec in self:
            for period in periods:
                schedule = rec.payment_ids.filtered(
                    lambda r: r.period_id == period)
                if not schedule:
                    raise ValidationError(
                        'Payment schedule not found for loan %s for '
                        'period %s' % (rec.name, period.name))
                schedule.write({
                    'pre_paid': True,
                    'amendment_id': amendment_id
                })

    @api.model
    def _needaction_domain_get(self):
        domain = []
        if self.env['res.users'].has_group('hr.group_hr_manager'):
            domain = [('state', '=', 'draft')]
        return domain

    @api.model
    def create_payment_amendment(self, period_id, employee_ids):
        amendment_obj = self.env['hr.payslip.amendment']
        payment_obj = self.env['hr.payroll.loan.payment']

        # let's get all scheduled payments in this period
        payments = payment_obj.search([
            ('period_id', '=', period_id),
            ('loan_id.employee_id', 'in', employee_ids),
            ('loan_id.state', '=', 'open'),
        ])

        if not payments:
            return

        amendments = payments.mapped('amendment_id').with_context(
            force_remove=True)
        amendments.unlink()

        for payment in payments:
            # create payslip amnedment of employee
            loan = payment.loan_id
            if loan.employee_id.identification_id:
                name = _('Loan Repayment: %s (%s)') % (
                    loan.employee_id.name, loan.employee_id.identification_id)
            else:
                name = _('Loan Repayment: %s') % (loan.employee_id.name,)

            vals = {
                'name': name,
                'employee_id': loan.employee_id.id,
                'amount': payment.amount,
                'hr_period_id': period_id,
                'note': 'Deduction made for loan payment (%s)' % loan.name,
                'category_id': loan.type_id.amendment_category_id.id,
            }

            amendment = amendment_obj.create(vals)
            amendment.signal_workflow('validate')
            payment.amendment_id = amendment.id
        return
