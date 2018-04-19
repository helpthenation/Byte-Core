# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import ValidationError, UserError
import pytz


class HotelFolio(models.Model):

    _inherit = 'hotel.folio'
    _order = 'reservation_id desc'

    reservation_id = fields.Many2one('hotel.reservation',
                                     string='Booking Id')
    parent_id = fields.Many2one('hotel.folio', string='Parent Folio', ondelete='cascade')
    child_ids = fields.One2many('hotel.folio', 'parent_id', string='Children Folios')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))

    @api.multi
    def write(self, vals):
        self.ensure_one()
        context = dict(self._context)
        if not context:
            context = {}
        context.update({'from_reservation': True})
        res = super(HotelFolio, self).write(vals)
        reservation_line_obj = self.env['hotel.room.reservation.line']
        for folio in self:
            if folio.reservation_id:
                for reservation in folio.reservation_id:
                    reservation_obj = (reservation_line_obj.search
                                       ([('reservation_id', '=',
                                          reservation.id)]))
                    if len(reservation_obj) == 1:
                        for line in reservation.group_room_reservation_ids:
                            vals = {'room_id': line.room_id.id,
                                    'check_in': line.folio.checkin_date,
                                    'check_out': line.folio.checkout_date,
                                    'state': 'assigned',
                                    'reservation_id': reservation.id,
                                    }
                            reservation_obj.write(vals)
        return res

    @api.constrains('room_lines')
    @api.one
    def folio_room_lines(self):
        rooms = [line.product_id.id for line in self.room_lines]
        for item in rooms:
            if rooms.count(item) > 1:
                raise ValidationError(_('You Cannot Allocate the Same Room Twice'))


class HotelFolioLineExt(models.Model):

    _inherit = 'hotel.folio.line'

    child_folio_id = fields.Many2one('hotel.folio', string='Folio')

    @api.constrains('checkin_date', 'checkout_date')
    def check_dates(self):
        if not self.folio_id.reservation_id.is_late_book:
            if self.checkin_date >= self.checkout_date:
                raise ValidationError(_('Room line Check In Date Should be \
                        less than the Check Out Date!'))
            if self.folio_id.date_order and self.checkin_date:
                if self.checkin_date <= self.folio_id.date_order:
                    raise ValidationError(_('Room line check in date should be \
                        greater than the current date.'))

    @api.onchange('checkin_date', 'checkout_date')
    def on_change_checkout(self):
        res = super(HotelFolioLineExt, self).on_change_checkout()
        hotel_room_obj = self.env['hotel.room']
        avail_prod_ids = []
        hotel_room_ids = hotel_room_obj.search([])
        for room in hotel_room_ids:
            assigned = False
            for line in room.reservation_line_ids:
                if line.status != 'cancel':
                    if(self.checkin_date <= line.check_in <=
                        self.checkout_date) or (self.checkin_date <=
                                                line.check_out <=
                                                self.checkout_date):
                        assigned = True
                    elif(line.check_in <= self.checkin_date <=
                         line.check_out) or (line.check_in <=
                                             self.checkout_date <=
                                             line.check_out):
                        assigned = True
            if not assigned:
                avail_prod_ids.append(room.product_id.id)
        return res

    @api.multi
    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        Update Hotel Room Booking line history"""
        reservation_line_obj = self.env['hotel.room.reservation.line']
        room_obj = self.env['hotel.room']
        prod_id = vals.get('product_id') or self.product_id.id
        chkin = vals.get('checkin_date') or self.checkin_date
        chkout = vals.get('checkout_date') or self.checkout_date
        is_reserved = self.is_reserved
        if prod_id and is_reserved:
            prod_domain = [('product_id', '=', prod_id)]
            prod_room = room_obj.search(prod_domain, limit=1)
            if (self.product_id and self.checkin_date and self.checkout_date):
                old_prd_domain = [('product_id', '=', self.product_id.id)]
                old_prod_room = room_obj.search(old_prd_domain, limit=1)
                if prod_room and old_prod_room:
                    # Check for existing room lines.
                    srch_rmline = [('room_id', '=', old_prod_room.id),
                                   ('check_in', '=', self.checkin_date),
                                   ('check_out', '=', self.checkout_date),
                                   ]
                    rm_lines = reservation_line_obj.search(srch_rmline)
                    if rm_lines:
                        rm_line_vals = {'room_id': prod_room.id,
                                        'check_in': chkin,
                                        'check_out': chkout}
                        rm_lines.write(rm_line_vals)
        return super(HotelFolioLineExt, self).write(vals)


class HotelReservation(models.Model):

    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Booking"
    _order = 'reservation_no desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    booking_mode = fields.Selection([('individual', 'Individual Booking'),
                                     ('group', 'Group Booking')],
                                    required=True,
                                    string='Booking Mode',
                                    readonly=True,
                                    states={'draft': [('readonly', False)]})
    folio_mode = fields.Selection([('group', 'Grouped Folio'),
                                   ('individual', 'Individual Folios')],
                                  readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  string='Folio Mode',
                                  default='group',
                                  help='Specify How Folio should be created for group booking'
                                       'Grouped Folio creates a single folio where all costs '
                                       'for rooms booked will be added'
                                       'Individual Folios create individual folios according to room lines')
    is_late_book = fields.Boolean(string='Late entry',
                                  readonly=True,
                                  help="Check this box if your'e entering booking which arrival date has past",
                                  default=False,
                                  states={'draft': [('readonly', False)]}

                                  )
    reservation_no = fields.Char(string='Booking No',
                                 size=64,
                                 readonly=True,
                                 help='Unique booking reference')
    date_order = fields.Datetime(string='Booking Date',
                                 readonly=True,
                                 required=True,
                                 index=True,
                                 default=(lambda *a: time.strftime(dt)),
                                 help='Date the booking was placed')
    warehouse_id = fields.Many2one('stock.warehouse',
                                   string='Hotel',
                                   readonly=True,
                                   index=True,
                                   required=True, default=1,
                                   states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner',
                                 string='Guest',
                                 readonly=True,
                                 index=True,
                                 states={'draft': [('readonly', False)]}
                                 )
    pricelist_id = fields.Many2one('product.pricelist',
                                   string='Price List',
                                   required=True,
                                   readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   help="Price list for current reservation.")
    partner_invoice_id = fields.Many2one('res.partner',
                                         string='Invoice Address',
                                         readonly=True,
                                         required=True,
                                         states={'draft':
                                                 [('readonly', False)]},
                                         help="Invoice address for "
                                         "current reservation.")
    partner_shipping_id = fields.Many2one('res.partner',
                                          string='Delivery Address',
                                          readonly=True,
                                          realated='partner_invoice_id',
                                          states={'draft':
                                                  [('readonly', False)]},
                                          help="Delivery address"
                                          "for current reservation. ")
    partner_order_id = fields.Many2one('res.partner',
                                       string='Group Contact',
                                       readonly=True,
                                       states={'draft':
                                               [('readonly', False)]},
                                       help="The name and address of the "
                                       "contact that requested the order "
                                       "or quotation.")
    checkin = fields.Datetime(string='Arrival Date', required=True,
                              readonly=True,
                              help="Date and time the guest is expected to arrive",
                              default=(lambda *a: datetime.strftime((datetime.strptime(time.strftime(dt),
                                                                                       dt)+timedelta(minutes=10)), dt)),
                              states={'draft': [('readonly', False)]})
    checkout = fields.Datetime(string='Departure Date',
                               required=True,
                               help="Date and time the guest is expected to leave",
                               readonly=True,
                               states={'draft': [('readonly', False)]})
    adults = fields.Integer('Adults', size=64, readonly=True,
                            required=True,
                            states={'draft': [('readonly', False)]},
                            help='Number of adults for this booking. ')
    children = fields.Integer(string='Children',
                              size=64,
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              help='Number of children for this booking.')
    room_id = fields.Many2one('hotel.room',
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              string='Room',
                              help='Select room for individual booking',
                              domain=[('status', '=', 'available')])
    group_room_reservation_ids = fields.One2many('hotel.reservation.line',
                                                 'reservation_id',
                                                 string="Group Room Booking",
                                                 help='Select the rooms for group booking')

    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('cancel', 'Cancelled'),
                              ('done', 'Done')],
                             string='State',
                             readonly=True,
                             default='draft')
    folio_ids = fields.Many2many('hotel.folio',
                                 'hotel_folio_reservation_rel',
                                 'order_id',
                                 'invoice_id',
                                 string='Folio')
    folio_number = fields.Integer(string='Folio(s)',
                                  compute='_compute_no_of_folios',
                                  help='Folio(s) related to this booking/reservation')
    dummy = fields.Datetime('Dummy')

    reserve_type = fields.Selection([('Walkin', 'Walk In'),
                                    ('Reservation', 'Reservation')],
                                    string='Booking Type',
                                    readonly=True,
                                    required=True,
                                    help='Select Walk In if the Guest is doing an immediate check in'
                                            'Select Reservation if guest making making a reservation to check in later',
                                    states={'draft': [('readonly', False)]})
    nights = fields.Integer(string='Enter Nights',
                            readonly=True,
                            help='Enter Number of Nights guest is staying for',
                            states={'draft': [('readonly', False)]})
    actual_nights = fields.Integer(string='Nights',
                                   help='Number of Nights guest is staying for',
                                   compute='compute_nights',
                                   readonly=True)
    separate_folios = fields.Boolean(string='Separate Folios',
                                     default=False,
                                     readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     help='Check this button if you want to create '
                                          'separate folios for this group booking'
                                     )
    separate_folio_cost = fields.Boolean(string='Individual Folio Invoice',
                                         default=False,
                                         help='Process sub folio costs and invoice separately',
                                         readonly=True,
                                         states={'draft': [('readonly', False)]})

    @api.onchange('booking_mode')
    @api.multi
    def onchange_booking_mode(self):
        self.ensure_one()
        for reservation in self:
            if reservation.booking_mode == 'individual':
                reservation.partner_order_id = False
                reservation.partner_invoice_id = False
                reservation.partner_shipping_id = False
                reservation.group_room_reservation_ids = False
            if reservation.booking_mode == 'group':
                reservation.room_id = False
                reservation.partner_id = False
                reservation.partner_order_id = False
                reservation.partner_invoice_id = False
                reservation.partner_shipping_id = False

    @api.onchange('checkin', 'checkout', 'nights')
    @api.multi
    def compute_nights(self):
        self.ensure_one()
        if self.checkin and self.checkout:
            diff = (datetime.strptime(self.checkout, dt) - datetime.strptime(self.checkin, dt)).days
            self.actual_nights = diff
        if self.nights >= 1 and self.checkin:
            checkout = datetime.strptime(self.checkin, dt)+timedelta(self.nights)
            self.checkout = checkout.strftime(dt)

    def _compute_no_of_folios(self):
        for rec in self:
            rec.folio_number = int(self.env['hotel.folio'].search_count([('reservation_id', '=', rec.id)]))
        return

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        self.ensure_one()
        for reserv_rec in self:
            if reserv_rec.state != 'draft':
                raise ValidationError(_('You cannot delete Booking in %s\
                                         state.') % (reserv_rec.state))
        return super(HotelReservation, self).unlink()

    @api.multi
    def copy(self):
        raise ValidationError(_('Sorry! you cannot Duplicate a Booking. Please create a new one instead'))

    @api.constrains('group_room_reservation_ids', 'room_id', 'adults', 'children')
    @api.multi
    def check_reservation_rooms(self):
        '''
        This method is used to validate the reservation_line.
        -----------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        '''
        self.ensure_one()
        ctx = dict(self._context) or {}
        for reservation in self:
            if reservation.booking_mode == 'individual':
                if not reservation.room_id:
                    raise ValidationError(_('Please Select rooms \
                                                    For group Booking.'))
                else:
                    if reservation.adults+reservation.children > reservation.room_id.capacity:
                        raise ValidationError(_('Room Capacity Exceeded \n Please \
                                                                            Select Room According to Members \
                                                                            Accommodation.'))

            if reservation.booking_mode == 'group':
                if not reservation.group_room_reservation_ids:
                    raise ValidationError(_('Please Select rooms \
                                    For group Booking.'))
                else:
                    capacity = 0
                    for line in reservation.group_room_reservation_ids:
                        capacity += line.room_id.capacity
                    if not ctx.get('duplicate'):
                        if (reservation.adults + reservation.children) > capacity:
                            raise ValidationError(_('Rooms Capacity Exceeded \n Please \
                                                    Select Rooms According to Members \
                                                    Accommodation.'))
            if reservation.adults <= 0:
                raise ValidationError(_('Adults must be greater than 0'))

            if reservation.group_room_reservation_ids:
                folio_rooms = []
                for line in reservation.group_room_reservation_ids:
                    if line.room_id.product_id.id in folio_rooms:
                        raise ValidationError(_('You Cannot Allocate Same Room Twice'))
                    folio_rooms.append(line.room_id.product_id.id)

    @api.constrains('checkin', 'checkout')
    def check_in_out_dates(self):
        """
        When date_order is less then check-in date or
        Checkout date should be greater than the check-in date.
        """
        if not self.is_late_book:
            if self.checkout and self.checkin:
                if self.checkin < self.date_order:
                    raise ValidationError(_('Check-in date should be greater than \
                                             the current date.'))
                if self.checkout < self.checkin:
                    raise ValidationError(_('Check-out date should be greater \
                                             than Check-in date.'))

    @api.model
    def _needaction_count(self, domain=None):
        """
         Show a count of draft state reservations on the menu badge.
         """
        return self.search_count([('state', '=', 'draft')])

    @api.onchange('partner_id', 'partner_order_id')
    @api.multi
    def onchange_partner_id(self):
        self.ensure_one()
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        '''
        if self.booking_mode == 'individual' and not self.partner_id:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
            self.partner_order_id = False
        if self.booking_mode == 'individual':
            addr = self.partner_id.address_get(['delivery', 'invoice',
                                                'contact'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id
        if self.booking_mode == 'group':
            addr = self.partner_order_id.address_get(['delivery', 'invoice'])
            self.partner_invoice_id = addr['invoice']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if not vals:
            vals = {}
        vals['reservation_no'] = vals['reserve_type'][0]+self.env['ir.sequence'].\
            next_by_code('hotel.reservation') or 'New'
        return super(HotelReservation, self).create(vals)

    @api.multi
    def check_overlap(self, date1, date2):
        date2 = datetime.strptime(date2, '%Y-%m-%d')
        date1 = datetime.strptime(date1, '%Y-%m-%d')
        delta = date2 - date1
        return set([date1 + timedelta(days=i) for i in range(delta.days + 1)])

    @api.multi
    def confirmed_reservation(self):
        self.ensure_one()
        """
        This method create a new record set for hotel room reservation line
        -------------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel room reservation line.
        """
        room_reservation_line_obj = self.env['hotel.room.reservation.line']
        for reservation in self:
            if reservation.booking_mode == 'individual':
                if reservation.room_id.status == 'available':
                    values = {'room_id': reservation.room_id.id,
                              'check_in': reservation.checkin,
                              'check_out': reservation.checkout,
                              'state': 'assigned',
                              'reservation_id': reservation.id,
                              }
                    reservation.room_id.write({'isroom': False, 'status': 'occupied'})
                    room_reservation_line_obj.create(values)
                    reservation.state = 'confirm'
            if reservation.booking_mode == 'group':
                if len(reservation.group_room_reservation_ids) < 2:
                    raise ValidationError('Group booking/reservation lines must be greater than 1. '
                                          'Otherwise create a single booking/reservation')
                if reservation.group_room_reservation_ids:
                    for line in reservation.group_room_reservation_ids:
                        if line.room_id.status == 'available':
                            values = {'room_id': line.room_id.id,
                                      'check_in': reservation.checkin,
                                      'check_out': reservation.checkout,
                                      'state': 'assigned',
                                      'reservation_id': reservation.id,
                                      }
                            line.room_id.write({'isroom': False, 'status': 'occupied'})
                            room_reservation_line_obj.create(values)
                            reservation.state = 'confirm'


        """
            for room in reservation.room_ids:
                if room.reservation_line_ids:
                    for line in room.reservation_line_ids.\
                            search([('status', 'in', ('confirm', 'done')),
                                    ('room_id', '=', room.id)]):
                        check_in = datetime.strptime(line.check_in, dt)
                        check_out = datetime.strptime(line.check_out, dt)
                        if check_in <= reserv_checkin <= check_out:
                            room_book = True
                        if check_in <= reserv_checkout <= check_out:
                            room_book = True
                        if reserv_checkin <= check_in and \
                                reserv_checkout >= check_out:
                            room_book = True
                        mytime = "%Y-%m-%d"
                        r_checkin = datetime.strptime(reservation.checkin,
                                                      dt).date()
                        r_checkin = r_checkin.strftime(mytime)
                        r_checkout = datetime.\
                            strptime(reservation.checkout, dt).date()
                        r_checkout = r_checkout.strftime(mytime)
                        check_intm = datetime.strptime(reservation.check_in,
                                                       dt).date()
                        check_outtm = datetime.strptime(reservation.check_out,
                                                        dt).date()
                        check_intm = check_intm.strftime(mytime)
                        check_outtm = check_outtm.strftime(mytime)
                        range1 = [r_checkin, r_checkout]
                        range2 = [check_intm, check_outtm]
                        overlap_dates = self.check_overlap(*range1) \
                            & self.check_overlap(*range2)
                        overlap_dates = [datetime.strftime(dates,
                                                           '%d/%m/%Y') for
                                         dates in overlap_dates]
                        if room_book:
                            raise ValidationError(_('You tried to Confirm '
                                                    'Booking with room'
                                                    ' those already '
                                                    'reserved in this '
                                                    'Booking Period. '
                                                    'Overlap Dates are '
                                                    '%s') % overlap_dates)
                        else:
                            self.state = 'confirm'
                            vals = {'room_id': room.id,
                                    'check_in': reservation.checkin,
                                    'check_out': reservation.checkout,
                                    'state': 'assigned',
                                    'reservation_id': reservation.id,
                                    }
                            room.write({'isroom': False,
                                           'status': 'occupied'})
                    else:
                        self.state = 'confirm'
                        vals = {'room_id': room.id,
                                'check_in': reservation.checkin,
                                'check_out': reservation.checkout,
                                'state': 'assigned',
                                'reservation_id': reservation.id,
                                }
                        room.write({'isroom': False,
                                       'status': 'occupied'})
                else:
                    self.state = 'confirm'
                    vals = {'room_id': room.id,
                            'check_in': reservation.checkin,
                            'check_out': reservation.checkout,
                            'state': 'assigned',
                            'reservation_id': reservation.id,
                            }
                    room.write({'isroom': False,
                                   'status': 'occupied'})
                room_reservation_line_obj.create(vals)
                """
        return True

    @api.multi
    def cancel_reservation(self):
        """
        This method cancel record set for hotel room reservation line
        ------------------------------------------------------------------
        @param self: The object pointer
        @return: cancel record set for hotel room reservation line.
        """
        room_res_line_obj = self.env['hotel.room.reservation.line']
        hotel_res_line_obj = self.env['hotel.reservation.line']
        room_reservation_line = room_res_line_obj.search([('reservation_id',
                                                           'in', self.ids)])
        room_reservation_line.write({'state': 'unassigned'})
        room_reservation_line.unlink()
        reservation_lines = hotel_res_line_obj.search([('reservation_id',
                                                        'in', self.ids)])
        for reservation_line in reservation_lines:
            reservation_line.write({'isroom': True,
                                            'status': 'available'})
        self.state = 'cancel'
        return True

    @api.multi
    def set_to_draft_reservation(self):
        self.state = 'draft'
        return True

    @api.multi
    def send_reservation_maill(self):
        '''
        This function opens a window to compose an email,
        template message loaded by default.
        @param self: object pointer
        '''
        assert len(self._ids) == 1, 'This is for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = (ir_model_data.get_object_reference
                           ('hotel_reservation',
                            'mail_template_hotel_reservation')[1])
        except ValueError:
            template_id = False
        try:
            compose_form_id = (ir_model_data.get_object_reference
                               ('mail',
                                'email_compose_message_wizard_form')[1])
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hotel.reservation',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_send': True,
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
            'force_send': True
        }

    @api.model
    def reservation_reminder_24hrs(self):
        """
        This method is for scheduler
        every 1day scheduler will call this method to
        find all tomorrow's reservations.
        ----------------------------------------------
        @param self: The object pointer
        @return: send a mail
        """
        now_str = time.strftime(dt)
        now_date = datetime.strptime(now_str, dt)
        ir_model_data = self.env['ir.model.data']
        template_id = (ir_model_data.get_object_reference
                       ('hotel_reservation',
                        'mail_template_reservation_reminder_24hrs')[1])
        template_rec = self.env['mail.template'].browse(template_id)
        for reserv_rec in self.search([]):
            checkin_date = (datetime.strptime(reserv_rec.checkin, dt))
            difference = relativedelta(now_date, checkin_date)
            if(difference.days == -1 and reserv_rec.partner_id.email and
               reserv_rec.state == 'confirm'):
                template_rec.send_mail(reserv_rec.id, force_send=True)
        return True

    @api.multi
    def create_folio(self):
        """
        This method is for create new hotel folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        self.ensure_one()
        hotel_folio_obj = self.env['hotel.folio']
        for reservation in self:
            checkin_date = reservation['checkin']
            checkout_date = reservation['checkout']
            if not self.checkin < self.checkout:
                raise ValidationError(_('Checkout date should be greater \
                                         than the Check-in date.'))
            duration_vals = (self.onchange_check_dates
                             (checkin_date=checkin_date,
                              checkout_date=checkout_date, duration=False))
            duration = duration_vals.get('duration') or 0.0
            if reservation.booking_mode == 'group' and len(reservation.group_room_reservation_ids) > 1:
                if reservation.separate_folios:
                    parent_folio = {
                        'date_order': reservation.date_order,
                        'warehouse_id': reservation.warehouse_id.id,
                        'pricelist_id': reservation.pricelist_id.id,
                        'partner_id': reservation.partner_order_id.id,
                        'partner_invoice_id': reservation.partner_invoice_id.id,
                        'partner_shipping_id': reservation.partner_shipping_id.id,
                        'checkin_date': reservation.checkin,
                        'checkout_date': reservation.checkout,
                        'duration': duration,
                        'reservation_id': reservation.id,
                        'service_lines': reservation['folio_ids']
                    }
                    p_folio = hotel_folio_obj.create(parent_folio)

                    for line in reservation.group_room_reservation_ids:
                        folio_lines = []
                        child_folio = {
                            'date_order': reservation.date_order,
                            'warehouse_id': reservation.warehouse_id.id,
                            'pricelist_id': reservation.pricelist_id and reservation.pricelist_id.id or 1,
                            'partner_id': line.partner_id.id,
                            'partner_invoice_id': reservation.partner_invoice_id.id,
                            'partner_shipping_id': reservation.partner_shipping_id.id,
                            'checkin_date': reservation.checkin,
                            'checkout_date': reservation.checkout,
                            'duration': duration,
                            'reservation_id': reservation.id,
                            'service_lines': reservation['folio_ids'],
                            'parent_id': p_folio.id
                        }
                        folio_lines.append((0, 0, {
                            'checkin_date': checkin_date,
                            'checkout_date': checkout_date,
                            'product_id': line.room_id and line.room_id.product_id.id,
                            'name': reservation['reservation_no'],
                            'price_unit': line.room_id.list_price,
                            'product_uom_qty': duration,
                            'is_reserved': True}))

                        child_folio.update({'room_lines': folio_lines})
                        p_folio.update({'room_lines': folio_lines})
                        child_folio = hotel_folio_obj.create(child_folio)
                        for room in child_folio.room_lines:
                            room.child_folio_id = child_folio.id
                    if p_folio:
                        for rm_line in p_folio.room_lines:
                            rm_line.product_id_change()
                    self._cr.execute('insert into hotel_folio_reservation_rel'
                                     '(order_id, invoice_id) values (%s,%s)',
                                     (reservation.id, p_folio.id))
                    reservation.state = 'done'

                if not reservation.separate_folios:
                    folio_lines = []
                    single_folio = {
                        'date_order': reservation.date_order,
                        'warehouse_id': reservation.warehouse_id.id,
                        'pricelist_id': reservation.pricelist_id.id,
                        'partner_id': reservation.partner_order_id.id,
                        'partner_invoice_id': reservation.partner_invoice_id.id,
                        'partner_shipping_id': reservation.partner_shipping_id.id,
                        'checkin_date': reservation.checkin,
                        'checkout_date': reservation.checkout,
                        'duration': duration,
                        'reservation_id': reservation.id,
                        'service_lines': reservation['folio_ids']
                    }
                    for line in reservation.group_room_reservation_ids:
                        folio_lines.append((0, 0, {
                            'checkin_date': checkin_date,
                            'checkout_date': checkout_date,
                            'product_id': line.room_id and line.room_id.product_id.id,
                            'name': reservation['reservation_no'],
                            'price_unit': line.room_id.list_price,
                            'product_uom_qty': duration,
                            'is_reserved': True}))
                        single_folio.update({'room_lines': folio_lines})
                    s_folio = hotel_folio_obj.create(single_folio)
                    if s_folio:
                        for rm_line in s_folio.room_lines:
                            rm_line.product_id_change()
                    self._cr.execute('insert into hotel_folio_reservation_rel'
                                     '(order_id, invoice_id) values (%s,%s)',
                                     (reservation.id, s_folio.id))
                    reservation.state = 'done'
            if reservation.booking_mode == 'individual' and reservation.room_id:
                folio_lines = []
                folio = {
                    'date_order': reservation.date_order,
                    'warehouse_id': reservation.warehouse_id.id,
                    'partner_id': reservation.partner_id.id,
                    'pricelist_id': reservation.pricelist_id.id,
                    'partner_invoice_id': reservation.partner_invoice_id.id,
                    'partner_shipping_id': reservation.partner_invoice_id.id,
                    'checkin_date': reservation.checkin,
                    'checkout_date': reservation.checkout,
                    'duration': duration,
                    'reservation_id': reservation.id,
                    'service_lines': reservation['folio_ids'],
                }
                folio_lines.append((0, 0, {
                    'checkin_date': checkin_date,
                    'checkout_date': checkout_date,
                    'product_id': reservation.room_id and reservation.room_id.product_id.id,
                    'name': reservation['reservation_no'],
                    'price_unit': reservation.room_id.list_price,
                    'product_uom_qty': duration,
                    'is_reserved': True}))
                folio.update({'room_lines': folio_lines})
                folio_id = hotel_folio_obj.create(folio)
                if folio_id:
                    for rm_line in folio_id.room_lines:
                        rm_line.product_id_change()
                self._cr.execute('insert into hotel_folio_reservation_rel'
                                 '(order_id, invoice_id) values (%s,%s)',
                                 (reservation.id, folio_id.id))
                reservation.state = 'done'
        return True

    @api.multi
    def onchange_check_dates(self, checkin_date=False, checkout_date=False,
                             duration=False):
        '''
        This method gives the duration between check in checkout if
        customer will leave only for some hour it would be considers
        as a whole day. If customer will checkin checkout for more or equal
        hours, which configured in company as additional hours than it would
        be consider as full days
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        '''
        value = {}
        configured_addition_hours = 0
        wc_id = self.warehouse_id
        whcomp_id = wc_id or wc_id.company_id
        if whcomp_id:
            configured_addition_hours = wc_id.company_id.additional_hours
        duration = 0
        if checkin_date and checkout_date:
            chkin_dt = datetime.strptime(checkin_date, dt)
            chkout_dt = datetime.strptime(checkout_date, dt)
            dur = chkout_dt - chkin_dt
            duration = dur.days + 1
            if configured_addition_hours > 0:
                additional_hours = abs((dur.seconds / 60))
                if additional_hours <= abs(configured_addition_hours * 60):
                    duration -= 1
        value.update({'duration': duration})
        return value


class HotelReservationLine(models.Model):

    _name = "hotel.reservation.line"
    _description = "Booking Line"

    reservation_id = fields.Many2one('hotel.reservation', readonly=False)
    room_id = fields.Many2one('hotel.room',
                              string='Room',
                              help='Select room',
                              domain="[('status','=', 'available'), ('isroom','=',True), ('categ_id','=', categ_id)]",
                              required=True)
    partner_id = fields.Many2one('res.partner', string='Guest', help='Select Guest', required=True)
    note = fields.Text(string='Note', help='Add notes if applicable')
    categ_id = fields.Many2one('hotel.room.type', string='Room Type', required=True)

    @api.constrains('categ_id', 'room_id')
    def check_room_and_category(self):
        if self.room_id and self.categ_id:
            if self.room_id.categ_id.id != self.categ_id.id:
                self.room_id = False
                self.categ_id = False
                raise ValidationError('Room Must match room category')

    @api.onchange('categ_id')
    def on_change_categ(self):
        '''
        When you change categ_id it check checkin and checkout are
        filled or not if not then raise warning
        -----------------------------------------------------------
        @param self: object pointer
        '''
        hotel_room_obj = self.env['hotel.room']
        hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
                                                 self.categ_id.id)])
        room_ids = []
        if not self.reservation_id.checkin:
            raise ValidationError(_('Before choosing a room,\n You have to \
                                     select a Check in date or a Check out \
                                     date in the booking form.'))
        for room in hotel_room_ids:
            assigned = False
            for line in room.reservation_line_ids:
                if line.status != 'cancel':
                    if(self.reservation_id.checkin <= line.check_in <=
                        self.reservation_id.checkout) or (self.reservation_id.checkin <=
                                                          line.check_out <=
                                                          self.reservation_id.checkout):
                        assigned = True
                    elif(line.check_in <= self.reservation_id.checkin <=
                         line.check_out) or (line.check_in <=
                                             self.reservation_id.checkout <=
                                             line.check_out):
                        assigned = True
            for rm_line in room.room_line_ids:
                if rm_line.status != 'cancel':
                    if(self.reservation_id.checkin <= rm_line.check_in <=
                       self.reservation_id.checkout) or (self.reservation_id.checkin <=
                                                         rm_line.check_out <=
                                                         self.reservation_id.checkout):
                        assigned = True
                    elif(rm_line.check_in <= self.reservation_id.checkin <=
                         rm_line.check_out) or (rm_line.check_in <=
                                                self.reservation_id.checkout <=
                                                rm_line.check_out):
                        assigned = True
            if not assigned:
                room_ids.append(room.id)
        domain = {'room_id': [('id', 'in', room_ids)]}
        return {'domain': domain}

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        hotel_room_reserv_line_obj = self.env['hotel.room.reservation.line']
        for line in self:
            hres_arg = [('room_id', '=', line.room_id.id),
                        ('reservation_id', '=', line.reservation_id.id)]
            myobj = hotel_room_reserv_line_obj.search(hres_arg)
            if myobj:
                for room_line in myobj:
                    room_line.room_id.write({'isroom': True, 'status': 'available'})
                    room_line.unlink()
        return super(HotelReservationLine, self).unlink()


class HotelRoomReservationLine(models.Model):

    _name = 'hotel.room.reservation.line'
    _description = 'Hotel Room Booking'
    _rec_name = 'room_id'

    room_id = fields.Many2one('hotel.room', string='Room id')
    check_in = fields.Datetime('Check In Date', required=True)
    check_out = fields.Datetime('Check Out Date', required=True)
    state = fields.Selection([('assigned', 'Assigned'),
                              ('unassigned', 'Unassigned')], 'Room Status')
    reservation_id = fields.Many2one('hotel.reservation',
                                     string='Booking')
    status = fields.Selection(string='state', related='reservation_id.state')
    folio_id = fields.Many2one(string='Folio',
                               help='Folio related to this room reservation Line')


class HotelRoom(models.Model):

    _inherit = 'hotel.room'
    _description = 'Hotel Room'

    reservation_line_ids = fields.One2many('hotel.room.reservation.line',
                                           'room_id',
                                           string='Room Reserve Line')

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        self.ensure_one()
        for room in self:
            for reserv_line in room.reservation_line_ids:
                if reserv_line.status == 'confirm':
                    raise ValidationError(_('Unable to delete a room with reservation in %s state')
                                          % reserv_line.status)
        return super(HotelRoom, self).unlink()

    @api.model
    def cron_room_line(self):
        """
        This method is for scheduler
        every 1min scheduler will call this method and check Status of
        room is occupied or available
        --------------------------------------------------------------
        @param self: The object pointer
        @return: update status of hotel room reservation line
        """

        for room in self.search([]):
            if room.reservation_line_ids:
                for reservation in room.reservation_line_ids:
                    if reservation.state:
                        pass

        reservation_line_obj = self.env['hotel.room.reservation.line']
        folio_room_line_obj = self.env['folio.room.line']
        now = datetime.now()
        curr_date = now.strftime(dt)
        for room in self.search([]):
            reserv_line_ids = [reservation_line.id for
                               reservation_line in
                               room.reservation_line_ids]
            reserv_args = [('id', 'in', reserv_line_ids),
                           ('check_in', '<=', curr_date),
                           ('check_out', '>=', curr_date)]
            reservation_line_ids = reservation_line_obj.search(reserv_args)
            rooms_ids = [room_line.id for room_line in room.room_line_ids]
            rom_args = [('id', 'in', rooms_ids),
                        ('check_in', '<=', curr_date),
                        ('check_out', '>=', curr_date)]
            room_line_ids = folio_room_line_obj.search(rom_args)
            status = {'isroom': True, 'color': 5}
            if reservation_line_ids.ids:
                status = {'isroom': False, 'color': 2}
            room.write(status)
            if room_line_ids.ids:
                status = {'isroom': False, 'color': 2}
            room.write(status)
            if reservation_line_ids.ids and room_line_ids.ids:
                raise ValidationError(_('Please Check Rooms Status \
                                         for %s.' % (room.name)))
        return True


class RoomReservationSummary(models.Model):

    _name = 'room.reservation.summary'
    _description = 'Room reservation summary'

    name = fields.Char('Booking Summary', default='Bookings Summary',
                       invisible=True)
    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date To')
    summary_header = fields.Text('Summary Header')
    room_summary = fields.Text('Room Summary')

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(RoomReservationSummary, self).default_get(fields)
        # Added default datetime as today and date to as today + 30.
        from_dt = datetime.today()
        dt_from = from_dt.strftime(dt)
        to_dt = from_dt + relativedelta(days=10)
        dt_to = to_dt.strftime(dt)
        res.update({'date_from': dt_from, 'date_to': dt_to})

        if not self.date_from and self.date_to:
            date_today = datetime.datetime.today()
            first_day = datetime.datetime(date_today.year,
                                          date_today.month, 1, 0, 0, 0)
            first_temp_day = first_day + relativedelta(months=1)
            last_temp_day = first_temp_day - relativedelta(days=1)
            last_day = datetime.datetime(last_temp_day.year,
                                         last_temp_day.month,
                                         last_temp_day.day, 23, 59, 59)
            date_froms = first_day.strftime(dt)
            date_ends = last_day.strftime(dt)
            res.update({'date_from': date_froms, 'date_to': date_ends})
        return res

    @api.multi
    def room_reservation(self):
        '''
        @param self: object pointer
        '''
        mod_obj = self.env['ir.model.data']
        if self._context is None:
            self._context = {}
        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'),
                                         ('name', '=',
                                          'view_hotel_reservation_form')])
        resource_id = model_data_ids.read(fields=['res_id'])[0]['res_id']
        return {'name': _('Reconcile Write-Off'),
                'context': self._context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hotel.reservation',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }

    @api.onchange('date_from', 'date_to')
    def get_room_summary(self):
        '''
        @param self: object pointer
         '''
        res = {}
        all_detail = []
        room_obj = self.env['hotel.room']
        reservation_line_obj = self.env['hotel.room.reservation.line']
        folio_room_line_obj = self.env['folio.room.line']
        user_obj = self.env['res.users']
        date_range_list = []
        main_header = []
        summary_header_list = ['Rooms']
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_('Please Check Time period Date From can\'t \
                                   be greater than Date To !'))
            if self._context.get('tz', False):
                timezone = pytz.timezone(self._context.get('tz', False))
            else:
                timezone = pytz.timezone('UTC')
            d_frm_obj = datetime.strptime(self.date_from, dt)\
                .replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            d_to_obj = datetime.strptime(self.date_to, dt)\
                .replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            temp_date = d_frm_obj
            while(temp_date <= d_to_obj):
                val = ''
                val = (str(temp_date.strftime("%a")) + ' ' +
                       str(temp_date.strftime("%b")) + ' ' +
                       str(temp_date.strftime("%d")))
                summary_header_list.append(val)
                date_range_list.append(temp_date.strftime
                                       (dt))
                temp_date = temp_date + timedelta(days=1)
            all_detail.append(summary_header_list)
            room_ids = room_obj.search([])
            all_room_detail = []
            for room in room_ids:
                room_detail = {}
                room_list_stats = []
                room_detail.update({'name': room.name or ''})
                if not room.reservation_line_ids and \
                   not room.room_line_ids:
                    for chk_date in date_range_list:
                        room_list_stats.append({'state': 'Free',
                                                'date': chk_date,
                                                'room_id': room.id})
                else:
                    for chk_date in date_range_list:
                        ch_dt = chk_date[:10] + ' 23:59:59'
                        ttime = datetime.strptime(ch_dt, dt)
                        c = ttime.replace(tzinfo=timezone).\
                            astimezone(pytz.timezone('UTC'))
                        chk_date = c.strftime(dt)
                        reserline_ids = room.reservation_line_ids.ids
                        reservline_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>=', chk_date),
                                            ('state', '=', 'assigned')
                                            ]))
                        if not reservline_ids:
                            sdt = dt
                            chk_date = datetime.strptime(chk_date, sdt)
                            chk_date = datetime.\
                                strftime(chk_date - timedelta(days=1), sdt)
                            reservline_ids = (reservation_line_obj.search
                                              ([('id', 'in', reserline_ids),
                                                ('check_in', '<=', chk_date),
                                                ('check_out', '>=', chk_date),
                                                ('state', '=', 'assigned')]))
                            for res_room in reservline_ids:
                                rrci = res_room.check_in
                                rrco = res_room.check_out
                                cid = datetime.strptime(rrci, dt)
                                cod = datetime.strptime(rrco, dt)
                                dur = cod - cid
                                if room_list_stats:
                                    count = 0
                                    for rlist in room_list_stats:
                                        cidst = datetime.strftime(cid, dt)
                                        codst = datetime.strftime(cod, dt)
                                        rm_id = res_room.room_id.id
                                        ci = rlist.get('date') >= cidst
                                        co = rlist.get('date') <= codst
                                        rm = rlist.get('room_id') == rm_id
                                        st = rlist.get('state') == 'Reserved'
                                        if ci and co and rm and st:
                                            count += 1
                                    if count - dur.days == 0:
                                        c_id1 = user_obj.browse(self._uid)
                                        c_id = c_id1.company_id
                                        con_add = 0
                                        amin = 0.0
                                        if c_id:
                                            con_add = c_id.additional_hours
#                                        When configured_addition_hours is
#                                        greater than zero then we calculate
#                                        additional minutes
                                        if con_add > 0:
                                            amin = abs(con_add * 60)
                                        hr_dur = abs((dur.seconds / 60))
#                                        When additional minutes is greater
#                                        than zero then check duration with
#                                        extra minutes and give the room
#                                        reservation status is reserved or
#                                        free
                                        if amin > 0:
                                            if hr_dur >= amin:
                                                reservline_ids = True
                                            else:
                                                reservline_ids = False
                                        else:
                                            if hr_dur > 0:
                                                reservline_ids = True
                                            else:
                                                reservline_ids = False
                                    else:
                                        reservline_ids = False
                        fol_room_line_ids = room.room_line_ids.ids
                        chk_state = ['draft', 'cancel']
                        folio_resrv_ids = (folio_room_line_obj.search
                                           ([('id', 'in', fol_room_line_ids),
                                             ('check_in', '<=', chk_date),
                                             ('check_out', '>=', chk_date),
                                             ('status', 'not in', chk_state)
                                             ]))
                        if reservline_ids or folio_resrv_ids:
                            room_list_stats.append({'state': 'Reserved',
                                                    'date': chk_date,
                                                    'room_id': room.id,
                                                    'is_draft': 'No',
                                                    'data_model': '',
                                                    'data_id': 0})
                        else:
                            room_list_stats.append({'state': 'Free',
                                                    'date': chk_date,
                                                    'room_id': room.id})

                room_detail.update({'value': room_list_stats})
                all_room_detail.append(room_detail)
            main_header.append({'header': summary_header_list})
            self.summary_header = str(main_header)
            self.room_summary = str(all_room_detail)
        return res


class QuickRoomReservation(models.TransientModel):
    _name = 'quick.room.reservation'
    _description = 'Quick Room Booking'

    partner_id = fields.Many2one('res.partner', string="Customer",
                                 required=True)
    check_in = fields.Datetime('Check In', required=True)
    check_out = fields.Datetime('Check Out', required=True)
    room_id = fields.Many2one('hotel.room', 'Room', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Hotel', required=True)
    pricelist_id = fields.Many2one('product.pricelist', 'pricelist')
    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address',
                                         required=True)
    partner_order_id = fields.Many2one('res.partner', 'Ordering Contact',
                                       required=True)
    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address',
                                          readonly=True,
                                          realated='partner_invoice_id',
                                          states={'draft':
                                                      [('readonly', False)]},
                                          help="Delivery address"
                                               "for current reservation. ")
    adults = fields.Integer('Adults', size=64, required=True)
    children = fields.Integer('Children', size=64)
    reserve_type = fields.Selection([('Walkin', 'Walk In'),
                                     ('Reservation', 'Reservation')],
                                    string='Booking Type',
                                    required=True,
                                    default='Walkin',
                                    help='Select Walk In if the Guest is doing an immediate check in'
                                         'Select Reservation if guest making making a reservation to check in later',
                                    states={'draft': [('readonly', False)]})

    @api.onchange('check_out', 'check_in')
    def on_change_check_out(self):
        '''
        When you change checkout or checkin it will check whether
        Checkout date should be greater than Checkin date
        and update dummy field
        -----------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        '''
        if self.check_out and self.check_in:
            if self.check_out < self.check_in:
                raise ValidationError(_('Checkout date should be greater \
                                         than Checkin date.'))

    @api.onchange('partner_id')
    def onchange_partner_id_res(self):
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        '''
        if not self.partner_id:
            self.partner_invoice_id = False
            self.partner_order_id = False
            self.partner_shipping_id = False
        else:
            addr = self.partner_id.address_get(['invoice',
                                                'contact',
                                                'delivery'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(QuickRoomReservation, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'date' in keys:
                res.update({'check_in': self._context['date']})
            if 'room_id' in keys:
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
        return res

    @api.multi
    def room_reserve(self):
        """
        This method create a new record for hotel.reservation
        -----------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel reservation.
        """
        hotel_res_obj = self.env['hotel.reservation']
        for res in self:
            rec = (hotel_res_obj.create
                   ({'partner_id': res.partner_id.id,
                     'reserve_type': res.reserve_type,
                     'partner_invoice_id': res.partner_invoice_id.id,
                     'partner_order_id': res.partner_order_id.id,
                     'partner_shipping_id': res.partner_shipping_id.id,
                     'checkin': res.check_in,
                     'checkout': res.check_out,
                     'warehouse_id': res.warehouse_id.id,
                     'pricelist_id': res.pricelist_id.id,
                     'adults': res.adults,
                     'children': res.children,
                     'booking_mode': 'individual',
                     'room_id': res.room_id.id
                     }))
        return rec
