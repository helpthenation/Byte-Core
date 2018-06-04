from odoo import models, api, fields
import json
from odoo.exceptions import ValidationError


class AutoTowingResource(models.Model):
    _inherit = ['ir.needaction_mixin']
    _name = 'auto.towing.resource'
    name = fields.Char(string='Name',
                       required=True,
                       index=True)
    mobile = fields.Char(string='Mobile #',
                         required=True)
    email = fields.Char(string='Email')
    dob = fields.Date(
        'Date of Birth'
    )

    auto_messiah_id = fields.Char(string='Auto Messiah ID',
                                  readonly=True,
                                  index=True,
                                  store=True)
    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female')
        ],
    )
    state = fields.Selection(
        [

            ('terminate', 'Terminated'),
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('boarding', 'On Boarding'),
            ('active', 'Active'),
        ],
        string='Internal State',
        default='draft',
        track_visibility='onchange'
    )

    towing_state = fields.Selection(
        [
            ('available', 'Available'),
            ('unavailable', 'Assigned'),
        ],
        string='Towing Sate',
        default='unavailable',
        track_visibility='onchange'
    )

    no_of_jobs = fields.Integer(string='Number of Jobs',
                                help='No of Jobs Completed',
                                readonly=True,
                                compute='_compute_no_of_jobs',
                                store=True)

    no_of_rating = fields.Integer(string='No. of Rating',
                                  readonly=True,
                                  help='Number of ratings')
    rating_score = fields.Integer(string='Rating Score',
                                  readonly=True)
    towing_request_ids = fields.One2many(comodel_name='auto.towing',
                                         inverse_name='towing_resource_id',
                                         name='Towing Requests')
    payment_ids = fields.One2many(comodel_name='auto.payment',
                                  inverse_name='towing_resource_id',
                                  name='Payment History')

    gps_location = fields.Char(string='Location Coordinate',
                               compute='compute_gps_location',
                               store=True,
                               readonly=True)
    gps_longitude = fields.Char(string='Location Longitude',
                                readonly=True)
    gps_latitude = fields.Char(string='Location Latitude',
                               readonly=True)

    is_company = fields.Boolean(string='Is a Company?', default=False,
                                help="Check if this is a company, otherwise it is a person")

    partner_type = fields.Selection(string='Partner Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    compute='_compute_partner_type', inverse='_write_partner_type')
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
    color = fields.Integer(string='Color Index',
                           compute='compute_color',
                           store=True)
    company_id = fields.Many2one(comodel_name='auto.towing.resource',
                                 string='Company')

    @api.depends('partner_type')
    @api.multi
    def compute_color(self):
        for rec in self:
            if rec.is_company:
                rec.color = 2
            else:
                rec.color = 0

    @api.depends('is_company')
    def _compute_partner_type(self):
        for partner in self:
            partner.partner_type = 'company' if partner.is_company else 'person'

    def _write_partner_type(self):
        for partner in self:
            partner.is_company = partner.partner_type == 'company'

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        self.is_company = (self.partner_type == 'company')

    @api.multi
    def compute_gps_location(self):
        self.ensure_one()
        for rec in self:
            maps_loc = {u'position': {u'lat': rec.gps_latitude, u'lng': rec.gps_longitude}, u'zoom': 3}
            json_map = json.dumps(maps_loc)
            self.gps_location = json_map

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """
        Redefine the search to search by towing resource name and id.
        """
        if not name:
            name = '%'
        if not args:
            args = []
        args = args[:]
        records = self.search(
            [
                '|',
                ('auto_messiah_id', operator, name),
                ('name', operator, name),
            ] + args,
            limit=limit
        )
        return records.name_get()

    @api.multi
    def set_draft(self):
        self.ensure_one()
        for rec in self:
            if rec.no_of_rating > 1:
                raise ValidationError('Cannot set Towing Resource to draft Partner already has completed jobs')
            else:
                rec.write({'state': 'draft'})

    @api.multi
    def set_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm'})

    @api.multi
    def set_on_board(self):
        for rec in self:
            rec.write({'state': 'boarding'})

    @api.multi
    def set_active(self):
        for rec in self:
            rec.write({'state': 'active'})

    def set_terminate(self):
        for rec in self:
            rec.write({'state': 'terminate'})
