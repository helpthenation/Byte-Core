from odoo import models, api, fields
import json
from odoo.exceptions import ValidationError


class StelmatMechanic(models.Model):
    _inherit = ['ir.needaction_mixin', 'res.partner']
    _name = 'auto.mechanic'
    dob = fields.Date(
        'Date of Birth'
    )

    identification_no = fields.Char(string='Mechanic ID',
                                    readonly=True,
                                    index=True,
                                    store=True
                                    )
    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female')
        ],
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('boarding', 'On Boarding'),
            ('active', 'Active'),
            ('terminate', 'Terminated'),
        ],
        string='Internal State',
        default='draft',
        track_visibility='onchange'
    )

    service_state = fields.Selection(
        [
            ('available', 'Available'),
            ('unavailable', 'Assigned'),
        ],
        string='Service Sate',
        default='unavailable',
        track_visibility='onchange'
    )

    no_of_jobs = fields.Integer(string='NNumber of Jobs',
                                help='No of Jobs Completed',
                                readonly=True,
                                compute='_compute_no_of_jobs',
                                store=True)

    no_of_rating = fields.Integer(string='No. of Rating',
                                  readonly=True,
                                  help='Number of ratings')
    rating_score = fields.Integer(string='Rating Score',
                                  readonly=True)

    gps_location = fields.Char(string='Location Coordinate',
                               compute='compute_gps_location',
                               store=True,
                               readonly=True)
    gps_longitude = fields.Char(string='Location Longitude',
                                readonly=True)
    gps_latitude = fields.Char(string='Location Latitude',
                               readonly=True)

    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', store=True, index=True)

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
        Redefine the search to search by driver name and id.
        """
        if not name:
            name = '%'
        if not args:
            args = []
        args = args[:]
        records = self.search(
            [
                '|',
                ('identification_no', operator, name),
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
                raise ValidationError('Cannot set mechanic to draft as he already has completed jobs')
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

    # Let's override parent class methods that are not necessary in this context
    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        pass

    @api.depends('company_name', 'parent_id.is_company', 'commercial_partner_id.name')
    def _compute_commercial_company_name(self):
        pass
