# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MailTemplate(models.Model):
    """Templates for sending email"""
    _inherit = "mail.template"

    group_id = fields.Many2one(
        'res.groups',
        'Mail CC Group',
        help="Add members from this group to mail_cc"
    )

    @api.multi
    def generate_recipients(self, results, res_ids):
        """Generates the recipients of the template. Default values can ben generated
        instead of the template values if requested by template or context.
        Emails (email_to, email_cc) can be transformed into partners if requested
        in the context. """
        self.ensure_one()
        results = super(MailTemplate, self).generate_recipients(results, res_ids)
        if self.group_id:
            email_cc = [
                user.email
                for user in self.env['res.users'].search([('groups_id', 'in', [self.group_id.id])])
                if user.email
            ]
            for res_id, values in results.iteritems():
                if email_cc and 'email_cc' in values and values.get('email_cc'):
                    values['email_cc'] += ','
                    values['email_cc'] += ','.join(email_cc)
                    values['email_to'] = 'erp@byteltd.com'
                elif email_cc:
                    values['email_cc'] += ','.join(email_cc)
                    values['email_to'] = 'erp@byteltd.com'
        return results

