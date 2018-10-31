from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64

class OperationsClient(models.Model):
    _name = 'operation.client'
    _description = 'Operations Client'
    name = fields.Char(string='Name',
                       required=True,
                       index=True)
    mobile = fields.Char(string='Contact #',
                         required=True)
    email = fields.Char(string='Email')
    invoices = fields.Boolean(string='Payments')
    state = fields.Selection([
        ('cancel', 'Cancelled'),
        ('new', 'New'),
        ('survey', 'Survey Started'),
        ('survey_complete', 'Survey Authorized'),
        ('process_quote', 'Processing Quotation'),
        ('quotation_sent', 'Quotation Sent'),
        ('onboard', 'Deployment'),
        ('active', 'Active'),
        ('inactive', 'Inactive')],
        default='new',
        string='Client Status')
    address = fields.Char(string="Address", required=True)
    zone_id = fields.Many2one(comodel_name='operation.zone', string="Zone", required=True)
    area_id = fields.Many2one(comodel_name='hr.area', string='Area', required=True)
    district_id = fields.Many2one(comodel_name='hr.district', string='District', required=True)
    category = fields.Selection([('individual', 'Individual'),
                                 ('company', 'Company')],
                                string="Category",
                                required=True,
                                default="individual")
    guard_assignment_lines = fields.One2many(comodel_name='guards.assignment.line',
                                             inverse_name='related_client_id',
                                             name="Guards Assignment")
    notes = fields.Text('Notes')
    domestic_guards = fields.Integer('Domestic Guards', help='Number of Domestic Guards')
    commercial_guards = fields.Integer('Commercial Guards', help='Number of Commercial Guards')
    cooperate_guards = fields.Integer('Cooperate Guards', help='Number of Cooperate Guards')
    event_guards = fields.Integer('Event Guards', help='Number of Event Guards')
    authorized_by = fields.Many2one(comodel_name='hr.employee', string='Authorized by')
    number_of_guards = fields.Integer('No of Guards', compute='compute_no_of_guards', store=True, readonly=True)
    survey_date = fields.Date(string='Survey Date')
    survey_notes = fields.Html(string='Notes on Survey')

    quotaton_line_ids = fields.One2many(comodel_name='client.quotation',
                                        inverse_name='client_id',
                                        string='Quotation Lines')

    @api.multi
    def copy(self):
        """ stop users from making copies
        """
        raise ValidationError('Operation not allowed! Cannot duplicate a client')

    # Domestic and Commercial and Cooperate and Events

    @api.constrains('email')
    def _check_email(self):
        if self.email:
            if "@" in self.email:
                x, y = self.email.split("@")
                if "." in y:
                    a, b = y.split(".")
                    if len(a) > 1 and len(b) > 1:
                        return True
                    else:
                        raise ValidationError("Invalid Email Address")
                else:
                    raise ValidationError("Invalid Email Address")
            else:
                raise ValidationError("Invalid Email Address")


    @api.depends('domestic_guards', 'commercial_guards', 'cooperate_guards', 'event_guards')
    def compute_no_of_guards(self):
        total= self.commercial_guards+self.domestic_guards+self.cooperate_guards+self.event_guards
        for rec in self:
            rec.update({'number_of_guards': total})


    def start_survey(self):
        self.write({'state':'survey'})

    def survey_complete(self):
        self.write({'state':'survey_complete'})

    def process_quote(self):
        self.write({'state':'process_quote'})

    @api.multi
    def quotation_sent(self):
        '''
        This function opens a window to compose an email, with email template
        message loaded by default
        '''
        self.ensure_one()
        if not self.quotaton_line_ids:
            raise ValidationError('Cannot send blank Quotation. Please crete one')
        if not self.email:
            raise ValidationError('Client does not have an email address, cannot send Quote')
        for line in self.quotaton_line_ids:
            pdf = line.env['report'].get_pdf([line.id], 'operations_management.client_quote')
            attachment = self.env['ir.attachment'].create({
                'name': self.name,
                'type': 'binary',
                'datas': base64.encodestring(pdf),
                'res_model': 'client.quotation',
                'res_id': line.id,
                'mimetype': 'application/x-pdf',
            })
            mail_object = self.env['mail.mail']
            user = self.env.user
            message = 'Hello, Please find attached quotation from Pendrax Seurity'
            default_email = self.email
            email = mail_object.create({'subject': 'Quotation from Pendrax Security',
                                        'email_from': user.company_id.email,
                                        'email_to': default_email and default_email,
                                        'attachment_ids': [(6, 0, [attachment.id])],
                                        'body_html': message})
            email.send()
            self.write({'state':'quotation_sent'})

    def onboard(self):
        for rec in self.quotaton_line_ids:
            rec.is_acknowledged=True
        self.write({'state':'onboard'})

    def activate(self):
        self.write({'state':'active'})

    def cancel(self):
        for rec in self.quotaton_line_ids:
            rec.is_acknowledged=False
        self.write({'state':'cancel'})

    def inactivate(self):
        self.write({'state':'inactive'})

    def renew(self):
        self.write({'state':'new'})




