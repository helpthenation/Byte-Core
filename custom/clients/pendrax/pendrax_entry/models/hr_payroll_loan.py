from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrPayrollLoan(models.Model):
    _inherit = 'hr.payroll.loan'

    confirmer_id = fields.Many2one('res.users', string='Corfirmer',
                                   default=lambda self: self.env.user.company_id.loan_confirmer_id)
    approver_id = fields.Many2one('res.users', string='Approver',
                                   default=lambda self: self.env.user.company_id.loan_approver_id)
    disburse_id = fields.Many2one('res.users', string='Disburser',
                                   default=lambda self: self.env.user.company_id.loan_disburse_id)
    state = fields.Selection(
        [
            ('draft', 'New'),
            ('wait_confirm', 'Awaiting Confirmation'),
            ('wait_approval', 'Awaiting Approval'),
            ('approved', 'Approved'),
            ('open', 'Disbursed'),
            ('cancel', 'Cancelled'),
            ('done', 'Payment Complete'),
        ],
        default='draft',
    )


    @api.multi
    def request_confirm(self):
        for rec in self:
            if len(rec.payment_ids)<1:
                raise ValidationError('You cannot request confirmation for a Loan that has no schedules,'
                                      'Click the Generate Schedule Button to Generte the schedules')
            rec.get_authorization('confirm')
            rec.write({'state':'wait_confirm'})


    @api.multi
    def request_approval(self):
        for rec in self:
            rec.get_authorization('approve')
            rec.write({'state':'wait_approval'})


    @api.multi
    def confirm_approval(self):
        for rec in self:
            rec.get_authorization('disburse')
            rec.write({'state':'approved'})

    @api.multi
    def get_authorization(self, resuest):
        subject=''
        body=''
        for rec in self:
            if resuest=='confirm':
                subject='Loan Confirmation'
                default_email = self.confirmer_id.email
                body='Dear ' + str(rec.confirmer_id.name) + " there is a new Loan request for "+str(rec.employee_id.name)\
                     +" with ID "+str(rec.employee_id.empid)+" awaiting your confirmation"\
                     +"\nLoan Type: "+str(rec.type_id.name)\
                +"\nTotal Amount Requested: "+str(rec.amount)\
                +"\nReference "+str(rec.name)
            if resuest=='approve':
                subject='Loan Approval'
                default_email = self.approver_id.email
                body='Dear ' + str(rec.approver_id.name) + " there is a new Loan request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+" awaiting your approval"\
                +"\nLoan Type: "+str(rec.type_id.name)\
                +"\nTotal Amount Requested: "+str(rec.amount)\
                +"\nReference "+str(rec.name)
            if resuest=='disburse':
                subject='Loan Disburse'
                default_email = self.disburse_id.email
                body='Dear ' + str(rec.disburse_id.name) + " there is a new Loan request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+" awaiting Disbursement"\
                +"\nLoan Type: "+str(rec.type_id.name)\
                +"\nTotal Amount Requested: "+str(rec.amount)\
                +"\nReference "+str(rec.name)


        mail_object = self.env['mail.mail']
        user = self.env.user

        email = mail_object.create({'subject': subject,
                                    'email_from': user.company_id.email,
                                    'email_to': default_email and default_email,
                                    'body_html': body})
        email.send()

    @api.multi
    def get_loan_approval(self):
        return self.env['report'].get_action(self, 'pendrax_entry.report_loan_approval')
