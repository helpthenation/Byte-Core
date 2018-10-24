from odoo import models, fields, api

class OperationsClient(models.Model):
    _name = "operations.client"
    _description = "Employee"
    name = fields.Char(string='Name',
                       required=True,
                       index=True)
    mobile = fields.Char(string='Contact #',
                         required=True)
    email = fields.Char(string='Email')
    invoices = fields.Boolean(string='Payments')
    state = fields.Selection([
        ('new', 'New'),
        ('survey', 'Conducting Survey'),
        ('quotation', 'Quotation'),
        ('onboard', 'Onboarding'),
        ('active', 'Active'),
        ('inactive', 'Inactive')],
        default='new',
        string='Client Status')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px", )
    address = fields.Char(string="Address", required=True)
    zone_id = fields.Many2one(comodel_name='operations.zone', string="Zone")
    category = fields.Selection([('individual', 'Individual'),
                                 ('company', 'Company')],
                                string="Category",
                                required=True,
                                default="individual")
    guard_assignment_lines = fields.One2many(comodel_name='guards.assignment.line',
                                             inverse_name='related_client_id',
                                             name="Guards Assignment")
    notes = fields.Text('Notes')

    def toggle_active(self):
        pass

    def start_survey(self):
        self.write({'state':'survey'})



    def start_quote(self):
        self.write({'state':'quotation'})

    def start_onboard(self):
        self.write({'state':'onboard'})

    def activate(self):
        self.write({'state':'active'})


