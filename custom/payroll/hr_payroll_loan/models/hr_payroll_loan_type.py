from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval as eval

_default_text_condition = '''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# job: hr.job object
# date_ref: date object of the date being considered may or may not be today
#          to be safe use in place of datetime.date.today()
# Note: returned value have to be set in the variable 'result'

result = job.id in (1, 2, 3)'''

_default_text_ceiling = '''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# job: hr.job object
# date_ref: date object of the date being considered may or may not be today
#          to be safe use in place of datetime.date.today()
# Note: returned value have to be set in the variable 'result'

result = contract.wage * 5'''


class hr_loan_type(models.Model):
    _name = "hr.payroll.loan.type"
    _description = "Employee Loan Type"

    _inherits = {'hr.payslip.amendment.category': "amendment_category_id"}

    provider = fields.Selection(
        [
            ('internal', 'Internal',),
            ('external', 'External')
        ],
        default='internal',
        required=True
    )
    provider_id = fields.Many2one(
        'res.partner',
        'Loan Provider'
    )
    rate = fields.Float(
        'Interest Rate',
        default=0.00
    )
    condition_select = fields.Selection(
        [
            ('none', 'Always True'),
            ('length', 'Service Length'),
            ('python', 'Python Expression')
        ],
        "Condition Based on",
        required=True,
        default='none'
    )
    condition_length_min = fields.Float(
        'Minimum Service Length',
        help="How long (months) must employee have been at the company before  "
        "qualifying for this loan type")
    condition_python = fields.Text(
        'Python Condition',
        help='Apply this rule for calculation if condition is true. '
             'You can specify condition like job.id in (1, 2, 3)',
        default=_default_text_condition
    )
    interval = fields.Integer(
        'Loan Intervals',
        help='How long (months) after a previous loan can employee request  '
             'for another. \n Zero means that another loan can\'t the running '
             'when this is requested.\nUse -1 to allow loan to run '
             'concurrently with others"'
    )
    interval_universal = fields.Boolean(
        'Consider Universal Periodity',
        help="Should interval take into consideration other loan types?",
    )
    payment_period = fields.Integer(
        'Maximum Payment Period',
        default=0.0,
        help="How long should (months) should loan payment take at maximum."

    )
    payment_ratio = fields.Float(
        'Maximum Payment to Wage Ratio',
        default=0.35,
        help="Ratio of payment amount to wage that should not be exceeded")
    ceiling = fields.Selection(
        [
            ('terminal', 'Terminal Benefit',),
            ('other', 'Other'),
            ('python', 'Python Code'),
            ('none', 'None')
        ],
        'Ceiling',
        required=True,
        default='none'
    )
    ceiling_python = fields.Text(
        'Python Ceiling',
        help='Evaluate this rule to get ceiling amount e.g.',
        default=_default_text_ceiling
    )
    ceiling_amount = fields.Float('Ceiling amount')

    amendment_category_id = fields.Many2one(
        'hr.payslip.amendment.category',
        'Amendment Category',
        readonly=True,
        ondelete='cascade',
        required=True,
        auto_join=True,
    )
    type = fields.Selection(
        [('add', 'Addition'), ('subtract', 'Deduction')],
        required=True,
        default='subtract'
    )
    defaults = {
        'type': 'subtract',
    }

    @api.model
    def create(self, vals):
        res = super(hr_loan_type, self).create(vals)
        res.amendment_category_id.type = 'subtract'
        return res

    @api.multi
    def unlink(self):
        self.mapped('amendment_category_id').unlink()
        return super(hr_loan_type, self).unlink()

    @api.multi
    def satisfy_condition(self, localdict):
        """
        @return: returns True if the given rule match the condition for the
                 employee. Return False otherwise.
        """
        self.ensure_one()
        employee = localdict['employee']
        if self.condition_select == 'none':
            return True
        elif self.condition_select == 'length':
            return employee.length_of_service >= self.condition_length_min
        else:  # python code
            try:
                eval(self.condition_python,
                     localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise UserWarning('Wrong python condition defined for '
                                  'loan type %s' % (self.name))

    @api.multi
    def check_interval_since_last(self, dt_str, employee_id):
        self.ensure_one()
        if self.interval < 0:
            return True
        dt_cmp = fields.Date.from_string(dt_str) - relativedelta(
            months=self.interval)
        domain = [
            ('state', '!=', 'cancel'),
            '|',
            ('date_closed', '>', fields.Date.to_string(dt_cmp)),
            ('date_closed', '=', False),
            ('employee_id', '=', employee_id),
        ]

        if not self.interval_universal:
            domain.append(('type_id', '=', self.id))

        if self.env['hr.payroll.loan'].search_count(domain) > 0:
            return False
        return True

    @api.multi
    def check_ceiling(self, amount, localdict):
        """
        @return: returns True if the given rule match the concondition_selectdition for the
                 given employee. Return False otherwise.
        """
        self.ensure_one()
        employee = localdict['employee']
        if self.ceiling == 'none':
            return True
        elif self.ceiling == 'other':
            return self.ceiling_amount >= amount
        elif self.ceiling == 'terminal':
            return employee.terminal_benefit >= amount
        else:  # python code
            try:
                eval(self.ceiling_python,
                     localdict, mode='exec', nocopy=True)
                result = 'result' in localdict and localdict['result'] or 0.0
                return result >= amount
            except:
                raise UserWarning('Wrong python condition defined for '
                                  'loan type %s' % (self.name))
