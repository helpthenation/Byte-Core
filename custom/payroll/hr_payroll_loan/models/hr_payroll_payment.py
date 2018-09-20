from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare


class HrLoanPayment(models.Model):
    _name = "hr.payroll.loan.payment"
    _description = "Loan Payment"
    _order = "id"

    name = fields.Char('Note', )
    loan_id = fields.Many2one(
        'hr.payroll.loan',
        'Loan',
        required=True,
        ondelete="cascade",
        index=True
    )
    period_id = fields.Many2one(
        'hr.period',
        'Pay Period',
        required=True
    )
    amendment_id = fields.Many2one(
        'hr.payslip.amendment',
        'Payslip Amendment',
        readonly=True,
    )
    pre_paid = fields.Boolean()
    paid = fields.Boolean(
        readonly=True,
        store=True,
        compute='_compute_paid_status'
    )
    amount = fields.Float(required=True)

    @api.depends('amendment_id', 'amendment_id.state', 'pre_paid')
    @api.one
    def _compute_paid_status(self):
        self.paid = (self.pre_paid or (bool(self.amendment_id)
                     and self.amendment_id.state == 'done'))

    @api.constrains('period_id', 'amendment_id')
    @api.multi
    def _constraint_period(self):
        self.ensure_one()
        for rec in self:
            if (rec.amendment_id
                    and rec.period_id != rec.amendment_id.hr_period_id):
                raise ValidationError(
                    'Period %s of the payment can not be different from that on '
                    'amendment %s' % (
                        rec.period_id.name, rec.amendment_id.hr_period_id.name))

    @api.multi
    @api.constrains('amount')
    def _payment_positive(self):
        self.ensure_one()
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Payment amount cannot be zero or negative')
            return True

    @api.model
    def create(self, data):
        loan = self.env['hr.payroll.loan'].browse(data['loan_id'])
        period = self.env['hr.period'].browse(data['period_id'])
        if 'name' not in data:
            data['name'] = '%s payment on %s' % (
                period.name,
                loan.name
            )
        if loan.balance < data['amount']:
            raise ValidationError(
                'Payment of %s for %s cannot be greater than loan  balance %s'
                % (data['amount'], loan.employee_id.name, loan.balance))
        precision = self.env['decimal.precision'].precision_get('Payroll')
        res = super(HrLoanPayment, self).create(data)
        if loan.state in ('open', 'draft') and float_is_zero(
                loan.balance, precision_digits=precision):
            loan.button_paid(dt=period.date_stop)

        return res

    @api.multi
    def write(self, vals):
        super(HrLoanPayment, self).write(vals)
        for payment in self:
            loan = payment.loan_id
            period = payment.period_id
            precision = self.env['decimal.precision'].precision_get('Payroll')
            if loan.state in ('open', 'draft') and float_is_zero(
                    loan.balance, precision_digits=precision):
                loan.button_paid(dt=period.date_stop)

    @api.multi
    def unlink(self):
        # if we are deleting a payment for a loan that was locked we should
        # open
        loans = self.mapped('loan_id').filtered(lambda r: r.state == 'done')
        loans.write({'state': 'open'})
        return super(HrLoanPayment, self).unlink()

    @api.multi
    def toggle_paid(self):
        self.ensure_one()
        self.write({'pre_paid': not self.pre_paid})

    @api.multi
    def mark_as_unpaid(self):
        self.ensure_one()
        self.write({'pre_paid': False})
