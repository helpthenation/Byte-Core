from odoo import fields, models, api
from odoo.exceptions import ValidationError
import time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    phone = fields.Char(string='Mobile #', required=True)
    nassit_no = fields.Char(string='Nassit Reg. #')
    labor_card_no = fields.Char(string='Labor Card #')
    p_address = fields.Char(string='Address')
    empid = fields.Char(string='ID', required=True)
    empid2 = fields.Char(string='Re-Enter ID', required=True)
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

    emergency_name = fields.Char(string='Emergency Contact Name')
    emergency_address = fields.Char(string='Emergency Contact Address')
    emergency_phone = fields.Char(string='Emergency Contact Phone')
    emergency_job = fields.Char(string='Emergency Contact Occupation')

    mother_name = fields.Char(string="Mother's Name")
    mother_address = fields.Char(string="Mother's Address")
    mother_phone = fields.Char(string="Mother's Phone")
    mother_job = fields.Char(string="Mother's Occupation")

    father_name = fields.Char(string="Father's Name")
    father_address = fields.Char(string="Father's Address")
    father_phone = fields.Char(string="Father's Phone")
    father_job = fields.Char(string="Father's Occupation")
    
    friend_name = fields.Char(string="Friend/Relative's Name")
    friend_address = fields.Char(string="Friend/Relative's Address")
    friend_phone = fields.Char(string="Friend/Relative's Phone")
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
    next_of_kin = fields.Char(string='Next of Kin Name')

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

    @api.depends('name')
    @api.multi
    def compute_create_date(self):
        for rec in self:
            rec.created_on = str(fields.Datetime.from_string(rec.create_date).strftime("%A %B %d"))

    @api.multi
    @api.constrains('empid', 'empid2')
    def check_id(self):
        for rec in self:
            if rec.empid != rec.empid2:
                raise ValidationError('ID not the Same Please Check')
