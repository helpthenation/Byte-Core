from odoo import models, fields, api


class HrPayrollLoan(models.Model):
    _inherit = 'hr.payroll.loan'

    confirmer_id = fields.Many2one('hr.employee', string='Corfirmer')
    approver_id = fields.Many2one('hr.employee', string='Approver')
    disburse_id = fields.Many2one('hr.employee', string='Disburser')
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
                default_email = self.confirmer_id.work_email
                body='Dear ' + str(rec.confirmer_id.name) + " there is a new Loan request "+str(rec.employee_id.name)
                +" awaiting your confirmation"+"\n"
                +"Loan Type: "+str(rec.type_id.name)+"\n"
                +"Total Amount Requested: "+str(rec.amount)+"\n"
                +"Reference "+str(rec.name)
            if resuest=='approve':
                subject='Loan Approval'
                default_email = self.approver_id.work_email
                body='Dear ' + str(rec.approver_id.name) + " there is a new Loan request "+str(rec.employee_id.name)
                +" awaiting your approval"+"\n"
                +"Loan Type: "+str(rec.type_id.name)+"\n"
                +"Total Amount Requested: "+str(rec.amount)+"\n"
                +"Reference "+str(rec.name)
            if resuest=='disburse':
                subject='Loan Disburse'
                default_email = self.disburse_id.work_email
                body='Dear ' + str(rec.disburse_id.name) + " there is a new Loan request "+str(rec.employee_id.name)
                +" awaiting Disbursement"+"\n"
                +"Loan Type: "+str(rec.type_id.name)+"\n"
                +"Total Amount Requested: "+str(rec.amount)+"\n"
                +"Reference "+str(rec.name)


        mail_object = self.env['mail.mail']
        user = self.env.user

        email = mail_object.create({'subject': subject,
                                    'email_from': user.company_id.email,
                                    'email_to': default_email and default_email,
                                    'body_html': body})
        email.send()
