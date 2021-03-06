from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class HrPayrollAllowance(models.Model):
    _name = 'hr.payroll.allowance'
    _order = "sequence"

    name = fields.Char(
        'Name',
        size=128,
        required=True
    )
    code = fields.Char(
        'Code',
        size=10,
        required=True
    )
    struct_id = fields.Many2one(
        'hr.payroll.structure',
        'Payroll Structure',
        required=True
    )
    in_report = fields.Boolean('Show in Reports')
    register_id = fields.Many2one(
        'hr.contribution.register',
        'Contribution Register',
        readonly=True
    )
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Salary Rule',
        readonly=True
    )
    taxexempt = fields.Boolean('Non-taxable Allowance')
    active = fields.Boolean(
        'Active',
        default=True
    )
    interval = fields.Selection(
        [
            ('each', 'Each Pay'),
            ('yearly', 'Once a Year'),
        ],
        'Payment Interval',
        required=True,
        default='each',
        help="Allowance is either paid with each slip or once a year")
    yearly_payment_strategy = fields.Selection(
        [
            ('anniversary', 'On Anniversary'),
            ('yearly', 'Start of Year'),
        ],
        'Payment Strategy',
        help="* Pay on the anniversary of employee's employment\n. "
             "* Pay at the beginning of the year"
    )
    yearly_payment_prorate = fields.Boolean(
        'Prorate',
        help="If we pay at the beginning of the year but employee is employed "
             "later in the year the allowance is paid based on the remaining "
             "months in the year")
    note = fields.Text('Description')
    sequence = fields.Integer(
        'Sequence',
        size=16,
        default=1
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda obj: obj.env.user.company_id
    )

    _sql_constraints = [
        ('allowance_code_uniq', 'unique(code)', 'Another allowance exists '
                                                'with this code'),
    ]

    @api.constrains('code')
    @api.multi
    def _check_code(self):
        rule_obj = self.env['hr.salary.rule']
        for allowance in self:
            domain = []
            if ' ' in allowance.code:
                raise ValidationError('Code cannot contain whitespace')
            domain.append(('code', '=', allowance.code))
            if allowance.rule_id:
                domain.append(('id', 'not in', (allowance.rule_id.id,)))
            if rule_obj.search_count(domain) > 0:
                raise ValidationError('Your Allowance Code Should be unique.')
        return True

    @api.model
    def get_allowances(self, company_id=None):
        '''
        get a list of all active allowances each as tuple in the form
        (name, code, field_name)
        '''
        company_id = company_id or self.env.user.company_id.id
        allowances = self.search([('company_id', '=', company_id),
                                  ('active', '=', True)])
        res = [(allowance.name, allowance.code,
                'x_' + allowance.code.lower() + '_amount')
               for allowance in allowances]
        return res

    @api.model
    def create(self, vals):
        res = super(HrPayrollAllowance, self).create(vals)
        rule_obj = self.env['hr.salary.rule']
        struct_obj = self.env['hr.payroll.structure']
        reg_obj = self.env['hr.contribution.register']

        update = {}
        # creating payroll fields
        note = vals.get('note', False)
        if note:
            note += ' - Auto created via payroll allowance'
        else:
            note = 'Auto created via payroll allowance'

        # let's create contribution register
        reg_name = 'Register for ' + vals['name']
        register = reg_obj.create({'name': reg_name})
        update['register_id'] = register.id

        # let's create a payroll rule for allowance
        category = (
            not vals.get('taxexempt', False) and self.env.ref('hr_payroll.ALW')
            or self.env.ref('hr_payroll_allowance.hr_categ_txexmptalw'))
        rule_data = {
            'code': vals['code'].upper(),
            'name': vals['name'],
            'category_id': category.id,
            'condition_select': 'python',
            'amount_select': 'code',
            'amount_python_compute':
                'result = contract.alw_amount_python_compute(payslip, "%s")'
                % (vals['code'].upper()),
            'register_id': register.id,
            'sequence': 50,
            'note': note,
            'condition_python':
                'result = contract.alw_condition_python(payslip, "%s")'
                % (vals['code'].upper()),
        }
        rule = rule_obj.create(rule_data)
        update['rule_id'] = rule.id

        # let's assign to salary structure
        struct = struct_obj.browse(vals['struct_id'])
        struct.write({'rule_ids': [(4, rule.id), ], })

        # lets update the allowance
        res.write(update)
        return res

    @api.multi
    def write(self, data):
        for allowance in self:
            if 'code' in data:
                raise Warning('Sorry, you can\'t edit the code once it has '
                              ' been created')
            # let's handle inactivation
            if 'active' in data:
                allowance.rule_id.active = data['active']

            # let's handl cases in which we change the base structur
            if 'struct_id' in data:
                allowance.struct_id.write(
                    {'rule_ids': [(3, allowance.rule_id.id), ], })
                struct = self.env['hr.payroll.structure'].browse(
                    data['struct_id'])
                struct.write({'rule_ids': [(4, allowance.rule_id.id), ], })

            if 'taxexempt' in data:
                category = (
                    not data['taxexempt'] and self.env.ref('hr_payroll.ALW')
                    or self.env.ref('l10n_sl_hr_payroll.hr_categ_txexmptalw'))
                allowance.rule_id.category_id = category.id

        return super(HrPayrollAllowance, self).write(data)

    @api.multi
    def copy(self):
        raise UserError('Salary allowance does not support duplication!')

    @api.multi
    def unlink(self):
        for allowance in self:
            allowance.rule_id.unlink()
            allowance.register_id.unlink()
        return super(HrPayrollAllowance, self).unlink()
