from odoo import models, fields, api, tools


class AutoUser(models.Model):
    _inherit = ['ir.needaction_mixin']
    _name = 'auto.user'
    name = fields.Char(string='Full Name',
                       required=True,
                       index=True)
    mobile = fields.Char(string='Mobile #',
                         required=True)
    email = fields.Char(string='Email')

    current_subscription_id = fields.Many2one(comodel_name='auto.subscription',
                                              string='Current Subscription',
                                              readonly=True)

    subscription_start_date = fields.Date(string='Start Date',
                                          related='current_subscription_id.start_date',
                                          help='Start Date of the current Subscription',
                                          readonly=True)
    subscription_expiry_date = fields.Date(string='Expiry Date',
                                           related='current_subscription_id.end_date',
                                           help='Expiry Date of the current Subscription',
                                           readonly=True)
    subscription_type_id = fields.Many2one(comodel_name='auto.subscription.type',
                                           related='current_subscription_id.subscription_type_id',
                                           help='Current Subscription Type',
                                           readonly=True)
    service_request_ids = fields.One2many(comodel_name='auto.service',
                                          inverse_name='related_user_id',
                                          name='Service Requests')
    towing_request_ids = fields.One2many(comodel_name='auto.towing',
                                         inverse_name='related_user_id',
                                         name='Towing Requests')
    payment_ids = fields.One2many(comodel_name='auto.payment',
                                  inverse_name='related_user_id',
                                  name='Payment History')
    state = fields.Selection([
                              ('suspended', 'Suspended'),
                              ('new', 'New'),
                              ('active', 'Active'),
                              ('expired', 'Subscription Expired')],
                             default='new',
                             string='User Status',
                             required=True)
    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female')
        ],
        string='Gender'
    )
    contact_person = fields.Char(string='Representative',
                                 help='Company Representative')
    representative_role = fields.Char(string="Rep's Role",
                                      help="Representative's Function")
    representative_phone = fields.Char(string="Rep's Contact #")
    company_address = fields.Char(string="Company's Address")
    company_website = fields.Char(string="Company's Website")
    comment = fields.Text(string='Internal Note')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px", )
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized image of this User. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized image of this User. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
    is_company = fields.Boolean(string='Is a Company?', default=False,
                                help="Check if this is a company, otherwise it is a person")

    user_type = fields.Selection(string='User Type',
                                 selection=[('person', 'Individual'), ('company', 'Company')],
                                 compute='_compute_user_type', inverse='_write_user_type')
    color = fields.Integer(string='Color Index',
                           compute='compute_color',
                           store=True)

    subscription_status = fields.Char(string='Subscription Status',
                                      store=True,
                                      compute='_compute_subscription_status')

    @api.depends('current_subscription_id')
    def _compute_subscription_status(self):
        for rec in self:
            if rec.current_subscription_id.state and rec.current_subscription_id.state == 'active':
                subscription_status = 'Active'
            else:
                subscription_status = 'Inactive'

    @api.depends('user_type')
    @api.multi
    def compute_color(self):
        for rec in self:
            if rec.is_company:
                rec.color = 2
            else:
                rec.color = 0

    @api.depends('is_company')
    def _compute_user_type(self):
        for user in self:
            user.user_type = 'company' if user.is_company else 'person'

    def _write_user_type(self):
        for user in self:
            user.is_company = user.user_type == 'company'

    @api.onchange('user_type')
    def onchange_user_type(self):
        self.is_company = (self.user_type == 'company')

    @api.model
    def _get_default_image(self):
        colorize, img_path, image = False, False, False

        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
        if image and colorize:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))

    @api.multi
    def set_active(self):
        for rec in self:
            rec.write({'state': 'active'})

    @api.multi
    def set_suspend(self):
        for rec in self:
            rec.write({'state': 'suspended'})
