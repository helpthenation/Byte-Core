from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    leave_allowance = fields.Float(string='Leave Allowance')
    confirmer_id = fields.Many2one('hr.employee', string='Leave Corfirmer',
                                   default=lambda self: self.env.user.company_id.leave_confirmer_id)
    approver_id = fields.Many2one('hr.employee', string='Leave Approver',
                                   default=lambda self: self.env.user.company_id.leave_approver_id)
    leave_allowance_disburser_id = fields.Many2one('hr.employee', string='Leave Allowance Disburser',
                                   default=lambda self: self.env.user.company_id.leave_allowance_disburser_id)
    f_approver = fields.Many2one('hr.employee', string='HOD')
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
    def get_authorization(self, request):
        subject=''
        body=''
        for rec in self:
            if request=='request':
                subject='Leave Request'
                default_email = rec.f_approver.work_email
                body='Dear ' + str(rec.f_approver.name) + " there is a new Leave request for "+str(rec.employee_id.name)\
                     +" with ID "+str(rec.employee_id.empid)+" awaiting your Validation"\
                     +"\nFrom: "+str(rec.date_from)\
                +"\nTo: "+str(rec.date_to)
            if request=='confirm':
                subject='Leave Confirmation'
                default_email = rec.confirmer_id.work_email
                body='Dear ' + str(rec.confirmer_id.name) + " there is a new Leave request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+" awaiting your Confirmation" \
                     + "\nFrom: " + str(rec.date_from) \
                     + "\nTo: " + str(rec.date_to)
            if request=='approve':
                subject='Leave Approval'
                default_email = rec.approver_id.work_email
                body='Dear ' + str(rec.approver_id.name) + " there is a new Leave request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+" awaiting Approval" \
                     + "\nFrom: " + str(rec.date_from) \
                     + "\nTo: " + str(rec.date_to)
            if request=='disburse':
                subject='Leave Allowance Request'
                default_email = rec.leave_allowance_disburser_id.work_email
                body='Dear ' + str(rec.leave_allowance_disburser_id.name) + " there is a new Leave request for "+str(rec.employee_id.name) \
                     + " with ID " + str(rec.employee_id.empid)+". PLease proceed with processing the leave allowance" \
                     + "\nFrom: " + str(rec.date_from) \
                     + "\nTo: " + str(rec.date_to)


        mail_object = self.env['mail.mail']
        user = self.env.user

        email = mail_object.create({'subject': subject,
                                    'email_from': user.company_id.email,
                                    'email_to': default_email and default_email,
                                    'body_html': body})
        email.send()

    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1', 'approve']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        return True

    @api.multi
    def action_validate(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))
            holiday.get_authorization('disburse')
            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [
                        (6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',  # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                # Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True