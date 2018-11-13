from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    confirmer_id = fields.Many2one('res.users', string='Leave Corfirmer',
                                   default=lambda self: self.env.user.company_id.leave_confirmer_id)
    approver_id = fields.Many2one('res.users', string='Leave Approver',
                                   default=lambda self: self.env.user.company_id.leave_approver_id)
    f_approver = fields.Many2one('res.users', string='HOD')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('approve', 'Awaiting HOD Validation'),
        ('confirm', 'Awaiting Confirmation'),
        ('cancel', 'Cancelled'),
        ('refuse', 'Refused'),
        ('validate1', 'Awaiting Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a holiday request is created." +
             "\nThe status is 'To Approve', when holiday request is confirmed by user." +
             "\nThe status is 'Refused', when holiday request is refused by manager." +
             "\nThe status is 'Approved', when holiday request is approved by manager.")


    @api.multi
    def request_hod_approval(self):
        for rec in self:
            rec.get_authorization('request')
            rec.write({'state':'approve'})


    @api.multi
    def request_confirm(self):
        for rec in self:
            rec.get_authorization('confirm')
            rec.write({'state':'confirm'})


    @api.multi
    def request_approval(self):
        for rec in self:
            rec.get_authorization('approve')
            rec.write({'state':'validate1'})

    @api.multi
    def get_authorization(self, resuest):
        subject=''
        body=''
        for rec in self:
            if resuest=='request':
                subject='Leave Request'
                default_email = self.f_approver.email
                body='Dear ' + str(rec.f_approver.name) + " there is a new Leave request for "+str(rec.employee_id.name)\
                     +" with ID "+str(rec.employee_id.empid)+" awaiting your Validation"\
                     +"\nFrom: "+str(rec.date_from)\
                +"\nTo: "+str(rec.date_to)
            if resuest=='confirm':
                subject='Leave Confirmation'
                default_email = self.confirmer_id.email
                body='Dear ' + str(rec.confirmer_id.name) + " there is a new Leave request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+" awaiting your Confirmation" \
                     + "\nFrom: " + str(rec.date_from) \
                     + "\nTo: " + str(rec.date_to)
            if resuest=='approve':
                subject='Leave Approval'
                default_email = self.approver_id.email
                body='Dear ' + str(rec.approver_id.name) + " there is a new Leave request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+" awaiting Approval" \
                     + "\nFrom: " + str(rec.date_from) \
                     + "\nTo: " + str(rec.date_to)


        mail_object = self.env['mail.mail']
        user = self.env.user

        email = mail_object.create({'subject': subject,
                                    'email_from': user.company_id.email,
                                    'email_to': default_email and default_email,
                                    'body_html': body})
        email.send()
