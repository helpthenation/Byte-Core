from odoo import fields, models, api
from odoo.exceptions import ValidationError
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from . import email_check


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _rec_name = 'name_and_id'
    name_and_id = fields.Char(compute='compute_name_id', store=True)
    phone = fields.Char(string='Mobile #', required=True)
    nassit_no = fields.Char(string='Nassit Reg. #')
    labor_card_no = fields.Char(string='Labor Card #')
    p_address = fields.Char(string='Address', required=True)
    empid = fields.Char(string='ID', required=True)
    length_current_Address = fields.Char(string='Length of Time at current address', required=True)
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    emp_date = fields.Date(string='Employment Date', required=True)
    tribe_id = fields.Many2one(comodel_name='hr.employee.tribe',
                               string='Tribe', required=True)
    religion_id = fields.Many2one(comodel_name='hr.employee.religion',
                                  string='Religion', required=True)
    place_of_birth_id = fields.Many2one(comodel_name='hr.employee.birthplace',
                                        string='Place of birth', required=True)
    height_ft = fields.Float(string='Height ft')
    height_in = fields.Float(string='Height Inches')

    spouse_name = fields.Char(string='Spouse Name')
    spouse_address = fields.Char(string='Spouse Address')
    spouse_phone = fields.Char(string='Spouse Phone')
    spouse_job = fields.Char(string='Spouse Occupation')

    emergency_name = fields.Char(string='Emergency Contact Name', required=True)
    emergency_address = fields.Char(string='Emergency Contact Address', required=True)
    emergency_phone = fields.Char(string='Emergency Contact Phone', required=True)
    emergency_job = fields.Char(string='Emergency Contact Occupation', required=True)

    mother_name = fields.Char(string="Mother's Name")
    mother_address = fields.Char(string="Mother's Address")
    mother_phone = fields.Char(string="Mother's Phone")
    mother_job = fields.Char(string="Mother's Occupation")

    father_name = fields.Char(string="Father's Name")
    father_address = fields.Char(string="Father's Address")
    father_phone = fields.Char(string="Father's Phone")
    father_job = fields.Char(string="Father's Occupation")
    
    friend_name = fields.Char(string="Friend/Relative's Name", required=True)
    friend_address = fields.Char(string="Friend/Relative's Address", required=True)
    friend_phone = fields.Char(string="Friend/Relative's Phone", required=True)
    friend_job = fields.Char(string="Friend/Relative's Occupation", required=True)
    
    nextofkin_name = fields.Char(string="Next of Kin's Name", required=True)
    nextofkin_address = fields.Char(string="Next of Kin's Address", required=True)
    nextofkin_phone = fields.Char(string="Next of Kin's Phone", required=True)
    nextofkin_relation = fields.Many2one(comodel_name='hr.employee.relation', string="Relation", required=True)

    history_ids = fields.One2many(comodel_name='hr.employee.history',
                                  inverse_name='employee_id',
                                  string='Employment History', required=True)
    academic_ids = fields.One2many(comodel_name='hr.employee.academic',
                                   inverse_name='employee_id',
                                   string='Academic History', required=True)
    reference_ids = fields.One2many(comodel_name='hr.employee.reference',
                                    inverse_name='employee_id',
                                    string='Professional References', required=True)

    criminal = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')],
                                string='Criminal Conviction',
                                default='no')
    illness = fields.Text(string='Illness/Disability that may affect Work', required=True)
    commitment = fields.Text(string='Commitment(s) that may affect Work', required=True)
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
                                      string='Region', required=True)
    age = fields.Integer('Age', compute='_compute_age', readonly=True, store=True)
    incomplete_info = fields.Boolean(string='Incomplete Info', default=False)
    deployment = fields.Char(string='Location')
    district_id = fields.Many2one(comodel_name='hr.district', string='District')
    fname = fields.Char(string='First Name', required=True)
    mname = fields.Char(string='Middle Name')
    lname = fields.Char(string='Last Name', required=True)
    refree_ids = fields.One2many(comodel_name='hr.employee.referee', inverse_name='employee_id', string='Refrees', required=True)
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
    @api.constrains('refree_ids', 'children_ids', 'reference_ids' 'academic_ids', 'spouse_name', 'work_email')
    def check_for_anomalies(self):
        for rec in self:
            if len(rec.refree_ids)<2:
                raise ValidationError("You must enter at least 2 Referees")
            if len(rec.reference_ids)<2:
                raise ValidationError("You must enter at least 2 Professional References")
            if len(rec.academic_ids)<1:
                raise ValidationError("You must enter at least 1 Academic History")
            if len(rec.children_ids)!=rec.children:
                raise ValidationError("Error!! You indicated "+str(rec.children)
                                      +" number of Children"+
                                      " but you've entered "+ str(len(rec.children_ids))+ " Children Details")
            if rec.marital=='married' and not rec.spouse_name:
                raise ValidationError("Please indicte your spouse info or change marital status")
            if rec.work_email and email_check.check_email(rec.work_email)==False:
                raise ValidationError("Invalid Work Email Address")







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
            rec.name_and_id = str(rec.name+" ("+rec.empid+")")
