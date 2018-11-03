from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'name'
    name = fields.Char(required=False, compute='compute_full_name', store=True)
    fname = fields.Char(string='First Name', required=True)
    mname = fields.Char(string='Middle Name')
    lname = fields.Char(string='Last Name', required=True)

    @api.multi
    @api.depends('fname','mname','lname')
    def compute_full_name(self):
        for rec in self:
            if rec.mname:
                rec.name = str(rec.fname)+" "+ str(rec.mname)+" "+str(rec.lname)
            else:
                rec.name = str(rec.fname) + " " + str(rec.lname)
            if rec.resource_id:
                rec.resource_id.name = rec.name

