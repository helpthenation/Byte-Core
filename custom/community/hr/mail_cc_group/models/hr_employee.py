from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def mail_copy_hr(self, mail_template, obj=None, force_send=False, raise_exception=False):
        """
        Email sending utility to send email to certain elements of an employee's network
        :param mail_template: email template to use
        :return:
        """
        user_obj = self.env['res.users']
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

        for employee in self:
            obj = obj or employee
            email_cc = [
                user.email
                for user in user_obj.search([('groups_id', 'in', [self.env.ref('hr.group_hr_user').id])])
            ]

            # create a mail_mail based on values, without attachments
            values = mail_template.generate_email(obj.id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            attachment_ids = values.pop('attachment_ids', [])
            attachments = values.pop('attachments', [])
            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')

            if email_cc and 'email_cc' in values and values.get('email_cc'):
                values['email_cc'] += ','
                values['email_cc'] += ','.join(email_cc)
            elif email_cc:
                values['email_cc'] += ','.join(email_cc)

            mail = Mail.create(values)

            # manage attachments
            for attachment in attachments:
                attachment_data = {
                    'name': attachment[0],
                    'datas_fname': attachment[0],
                    'datas': attachment[1],
                    'res_model': 'mail.message',
                    'res_id': mail.mail_message_id.id,
                }
                attachment_ids.append(Attachment.create(attachment_data).id)
            if attachment_ids:
                values['attachment_ids'] = [(6, 0, attachment_ids)]
                mail.write({'attachment_ids': [(6, 0, attachment_ids)]})

            if force_send:
                mail.send(raise_exception=raise_exception)







    @api.multi
    def force_payslip_send(self):
        for slip in self:
            email_act = slip.action_payslip_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                slip.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True