from odoo import fields, models, api
from odoo.exceptions import ValidationError, Warning as UserError
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from . import email_check


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _rec_name = 'name_and_id'
    name_and_id = fields.Char(compute='compute_name_id', store=True)
    phone = fields.Char(string='Mobile #')
    nassit_no = fields.Char(string='Nassit Reg. #')
    labor_card_no = fields.Char(string='Labor Card #')
    p_address = fields.Char(string='Address')
    empid = fields.Char(string='ID')
    length_current_Address = fields.Char(string='Length of Time at current address')
    date_of_birth = fields.Date(string='Date of Birth')
    emp_date = fields.Date(string='Employment Date')
    tribe_id = fields.Many2one(comodel_name='hr.employee.tribe',
                               string='Tribe')
    religion_id = fields.Many2one(comodel_name='hr.employee.religion',
                                  string='Religion')
    place_of_birth_id = fields.Many2one(comodel_name='hr.employee.birthplace',
                                        string='Place of birth')
    height_ft = fields.Float(string='Height ft')
    height_in = fields.Float(string='Height Inches')

    spouse_name = fields.Char(string='Spouse Name')
    spouse_address = fields.Char(string='Spouse Address')
    spouse_phone = fields.Char(string='Spouse Phone')
    spouse_job = fields.Char(string='Spouse Occupation')
    spouse_job_id = fields.Many2one(comodel_name='hr.occupation',string='Spouse Occupation')

    emergency_name = fields.Char(string='Emergency Contact Name')
    emergency_address = fields.Char(string='Emergency Contact Address')
    emergency_phone = fields.Char(string='Emergency Contact Phone')
    emergency_job_id = fields.Many2one(comodel_name='hr.occupation', string='Emergency Contact Occupation')
    emergency_job = fields.Char(string='Emergency Contact Occupation')

    mother_name = fields.Char(string="Mother's Name")
    mother_address = fields.Char(string="Mother's Address")
    mother_phone = fields.Char(string="Mother's Phone")
    mother_job = fields.Char(string="Mother's Occupation")
    mother_job_id = fields.Many2one(comodel_name='hr.occupation', string="Mother's Occupation")

    father_name = fields.Char(string="Father's Name")
    father_address = fields.Char(string="Father's Address")
    father_phone = fields.Char(string="Father's Phone")
    father_job_id = fields.Many2one(comodel_name='hr.occupation', string="Father's Occupation")
    father_job = fields.Char(string="Father's Occupation")

    friend_name = fields.Char(string="Friend/Relative's Name")
    friend_address = fields.Char(string="Friend/Relative's Address")
    friend_phone = fields.Char(string="Friend/Relative's Phone")
    friend_job_id = fields.Many2one(comodel_name='hr.occupation', string="Friend/Relative's Occupation")
    friend_job = fields.Char(string="Friend/Relative's Occupation")

    nextofkin_name = fields.Char(string="Next of Kin's Name")
    nextofkin_address = fields.Char(string="Next of Kin's Address")
    nextofkin_phone = fields.Char(string="Next of Kin's Phone")
    nextofkin_relation = fields.Many2one(comodel_name='hr.employee.relation', string="Relation")

    history_ids = fields.One2many(comodel_name='hr.employee.history',
                                  inverse_name='employee_id',
                                  string='Employment History')
    academic_ids = fields.One2many(comodel_name='hr.employee.academic',
                                   inverse_name='employee_id',
                                   string='Academic History')
    reference_ids = fields.One2many(comodel_name='hr.employee.reference',
                                    inverse_name='employee_id',
                                    string='Professional References')

    criminal = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')],
                                string='Criminal Conviction',
                                default='no')
    illness = fields.Text(string='Illness/Disability that may affect Work')
    commitment = fields.Text(string='Commitment(s) that may affect Work')
    support = fields.Text(string='Support Info. for application')
    reference = fields.Char(string='Pendrax ID',
                            default=lambda obj: obj.env['ir.sequence'].next_by_code('hr.employee'),
                            index=True,
                            readonly=True)
    children_ids = fields.One2many(comodel_name='hr.employee.children', inverse_name='employee_id',
                                   string='Children')
    created_on = fields.Char(string='Date Create',
                             compute='compute_create_date',
                             store=True,
                             readonly=True)
    passport = fields.Char(string='Passport/Permit No.')
    qualification = fields.Char(string='Professional Qualification/Training')
    staff_category = fields.Selection([('guard', 'Guard'),
                                      ('admin', 'Admin')],
                                      string='Payroll Category',
                                      required=True)
    staff_location = fields.Selection([('freetown', 'Freetown'),
                                      ('provincial', 'Provincial')],
                                      string='Region')
    age = fields.Integer('Age', compute='_compute_age', readonly=True, store=True)
    incomplete_info = fields.Boolean(string='Incomplete Info', default=False)
    deployment = fields.Char(string='Location')
    district_id = fields.Many2one(comodel_name='hr.district', string='District')
    area_id = fields.Many2one(comodel_name='hr.area', string='Area', required=True)
    refree_ids = fields.One2many(comodel_name='hr.employee.referee', inverse_name='employee_id', string='Refrees')
    mother_deceased = fields.Boolean(string="Mother Deceased", default=False)
    father_deceased = fields.Boolean(string="Father Deceased", default=False)
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female')],
                              required=True,
                              string='Gender')


    _sql_constraints = [
        ('unique_empid', 'unique (empid)', "Employee ID Already Exist !"),
    ]

    @api.multi
    @api.constrains('refree_ids', 'refree_ids.email', 'children_ids', 'reference_ids', 'reference_ids.email', 'academic_ids', 'spouse_name', 'work_email')
    def check_for_anomalies(self):
        for rec in self:
            if len(rec.refree_ids)<2 and rec.incomplete_info==False:
                raise ValidationError("You must enter at least 2 Referees")
            if len(rec.reference_ids)<2 and rec.incomplete_info==False:
                raise ValidationError("You must enter at least 2 Professional References")
            if len(rec.academic_ids)<1 and rec.incomplete_info==False:
                raise ValidationError("You must enter at least 1 Academic History")
            if len(rec.children_ids)!=rec.children:
                raise ValidationError("Error!! You indicated "+str(rec.children)
                                      +" number of Children"+
                                      " but you've entered "+ str(len(rec.children_ids))+ " Children Details")
            if rec.marital=='married' and not rec.spouse_name:
                raise ValidationError("Please indicte your spouse info or change marital status")
            if rec.work_email and email_check.check_email(rec.work_email)==False:
                raise ValidationError("Invalid Work Email Address")
            if len(rec.reference_ids)>0:
                for ref in rec.reference_ids:
                    if ref.email and email_check.check_email(ref.email) == False:
                        raise ValidationError("Invalid Email Address for Professional Reference "+str(ref.name))
            if len(rec.refree_ids)>0:
                for ref in rec.refree_ids:
                    if ref.email and email_check.check_email(ref.email) == False:
                        raise ValidationError("Invalid Email Address for Referee "+str(ref.name))








    @api.depends('name')
    @api.multi
    def compute_create_date(self):
        for rec in self:
            rec.created_on = str(fields.Datetime.from_string(rec.create_date).strftime("%A %B %d"))

    @api.multi
    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            rec.age = 0
            if rec.date_of_birth:
                start = datetime.strptime(rec.date_of_birth,
                                          DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                        DEFAULT_SERVER_DATE_FORMAT)
                age = ((end - start).days / 365)
                rec.age = age and age or 10

    @api.multi
    @api.depends('name', 'empid')
    def compute_name_id(self):
        for rec in self:
            if rec.empid:
                rec.name_and_id = str(rec.name+" ("+rec.empid +")")

    @api.multi
    def state_onboarding(self):
        # lets ensure that all have a complete info
        if self.incomplete_info:
            raise UserError(
                'You cannot confirm an employee that does not yet have Complete Information.')
        # lets ensure that all have a contract set
        if self.filtered(lambda r: not r.contract_ids):
            raise UserError(
                'You cannot confirm an employee that does not yet have an employment contract')
        self.write({'status': 'onboarding'})
