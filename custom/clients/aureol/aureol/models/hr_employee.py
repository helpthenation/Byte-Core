from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    aureol_staff_category = fields.Selection([('general', 'General staff'),
                                        ('management', 'Management staff')],
                                       string='Staff Category',
                                       required=True)
    er_number = fields.Char(string='ER Number', help='Employee Registration Number')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], groups='hr.group_hr_user', required=True)

    @api.multi
    def get_cummilative_details(self, run, date_start, date_stop):
        for rec in self:
            total_gross = 0.0
            total_paye = 0.0
            # lets get all periods in current FY
            all_periods = rec.env['hr.period'].search([('date_start','>=',date_start),
                                                        ('date_stop','<=',date_stop)],
                                                       order = 'date_start asc')
            # lets get all employee payslips
            payslips = rec.env['hr.payslip'].search([('employee_id','=',rec.id)])


            # Lets get cummilative
            for period in all_periods:
                slip = payslips.search([('hr_period_id', '=',period.id),('employee_id','=',rec.id)])
                if slip and run.same_gross and run.same_paye:
                    total_paye=slip.line_ids.filtered(lambda r: r.code == "PAYE").total*(len(all_periods))
                    total_gross=slip.line_ids.filtered(lambda r: r.code == "GROSS").total*(len(all_periods))
                    return [total_gross, total_paye]
                total_gross+=slip.line_ids.filtered(lambda r: r.code == "GROSS").total
                total_paye+=slip.line_ids.filtered(lambda r: r.code == "PAYE").total

            return [total_gross,total_paye]