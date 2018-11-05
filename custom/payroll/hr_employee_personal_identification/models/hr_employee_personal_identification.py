from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HrEmployeePersonalId(models.Model):
    _name = 'hr.employee.personal.id'
    employee_id = fields.Many2one('hr.employee', 'Employee',
                                  required=True,
                                  index=True,
                                  ondelete='cascade')
    notify_employee_id = fields.Many2one('hr.employee', 'Notify Who?',
                                  required=True,
                                  index=True,
                                  ondelete='cascade')
    id_type = fields.Many2one('hr.employee.personal.id.type', 'ID type',
                              required=True,
                              index=True)
    id_number = fields.Char('Identification Number',
                            required=True)
    expiry_date = fields.Date('Expiry Date', required=True)

    status = fields.Selection([('valid', 'Valid'),
                               ('expired', 'Expired'),],
                              string="Validity",
                              default='valid')
    expired_alert = fields.Boolean(string='Expired Alert', default=True, readonly=True)

    expiry_notification_days = fields.Integer(string='Expiry Notification Days', default=30)

    _sql_constraints = [('id_number', 'UNIQUE(id_number, id_type)', 'Identification type and number already Exist'),
                        ('employee_id', 'UNIQUE(employee_id, id_type)', 'Identification type already Exist')]


    @api.multi
    def send_expired_alert(self):
        self.ensure_one()
        for rec in self:
            mail_object = self.env['mail.mail']
            subject = rec.id_type.name+" Expired"
            message = "This is to notify you that "+\
                      rec.employee_id.name+"'s "+\
                      rec.id_type.name+" has expired. "+"Expiry date was "+str(rec.expiry_date)
            user = self.env.user
            default_email = self.notify_employee_id.work_email
            email = mail_object.create({'subject': subject,
                                        'email_from': user.company_id.email,
                                        'email_to': default_email and default_email,
                                        'body_html': message})
            email.send()

    @api.multi
    def send_expiry_notification(self, days):
        self.ensure_one()
        for rec in self:
            mail_object = self.env['mail.mail']
            subject = rec.id_type.name + " about to expire"
            message = "This is to notify you that " + \
                      rec.employee_id.name + "'s " + \
                      rec.id_type.name + " will expire in " +str(days)+ " days time. Expiry date is " + str(rec.expiry_date)
            user = self.env.user
            default_email = self.notify_employee_id.work_email
            email = mail_object.create({'subject': subject,
                                        'email_from': user.company_id.email,
                                        'email_to': default_email and default_email,
                                        'body_html': message})
            email.send()


    @api.multi
    def try_check_expiry(self):
        for rec in self.search([]):
            if rec.expiry_date and rec.expiry_notification_days:
                days = relativedelta(
                    fields.Date.from_string(rec.expiry_date),
                    fields.Date.from_string(fields.Date.today())).days
                if rec.expiry_notification_days >= days and days>=0:
                    rec.send_expiry_notification(days)
                if days<1:
                    rec.status='expired'
                    if rec.expired_alert:
                        rec.send_expired_alert()




