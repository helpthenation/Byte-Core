import time
from datetime import datetime
from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools import amount_to_text_en


class AureolNraReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AureolNraReport, self).__init__(cr, uid, name,
                                                    context=context)

        self.localcontext.update({
            'time': time,
            'get_month':self.get_month,
            'get_header_text':self.get_header_text,
            'get_footer_text':self.get_footer_text,
            'get_detail':self.get_detail,
            'get_totals':self.get_totals,

        })
        self.context = context
    def get_header_text(self, run_id):
        date = run_id.date_payment
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return "CONTRIBUTION SCHEDULE FOR THE MONTH OF " +date_dt.strftime("%B").upper()+", "+str(date_dt.year)

    def get_footer_text(self, run_id):
        date = run_id.date_payment
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return "I.........................................................hereby declare that the return is a true account " \
               "of all deductions/refunds of income tax made from the emoluments of employees for the month ended 30TH " +date_dt.strftime("%B").upper()+", "+str(date_dt.year)\
               +" in accordance with the table of monthly deductions and enclose cash/cheque remittance totalling "


    def get_month(self, run_id):
        date = run_id.date_payment
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return date_dt.strftime("%B").upper()


    def convert(self, amount, cur):
        return amount_to_text_en.amount_to_text(amount, 'en', cur)

    def get_totals(self, slip_ids):
        total_paye = 0.0
        total_gross = 0.0
        total_cumm_paye = 0.0
        total_cumm_gross = 0.0
        for s in slip_ids:
            gross = s.line_ids.filtered(lambda r: r.code == "GROSS").total,
            paye = s.line_ids.filtered(lambda r: r.code == "PAYE").total * -1,
            cumm_gross = s.employee_id.get_cummilative_details(s.hr_period_id.fiscalyear_id.date_start, s.date_to)[
                              0]  or "",
            cumm_paye = s.employee_id.get_cummilative_details(s.hr_period_id.fiscalyear_id.date_start, s.date_to)[
                             -1] * -1 or "",
            total_paye+=paye[0]
            total_gross+=gross[0]
            total_cumm_paye+=cumm_paye[0]
            total_cumm_gross+=cumm_gross[0]
        return {
                'name': "TOTAL",
                'total_paye': total_paye,
                'total_gross': total_gross,
                'total_cumm_paye': total_cumm_paye,
                'total_cumm_gross': total_cumm_gross,}

    def get_detail(self, slip_ids):
        result = []
        for s in slip_ids:
            gross = s.line_ids.filtered(lambda r: r.code == "GROSS").total,
            paye = s.line_ids.filtered(lambda r: r.code == "PAYE").total * -1,
            cumm_gross = s.employee_id.get_cummilative_details(s.hr_period_id.fiscalyear_id.date_start, s.date_to)[
                              0] or "",
            cumm_paye = s.employee_id.get_cummilative_details(s.hr_period_id.fiscalyear_id.date_start, s.date_to)[
                             -1] * -1 or "",
            result.append({
                'name': s.employee_id.name or "",
                'gross': gross,
                'paye': paye,
                'cumm_gross': cumm_gross,
                'cumm_paye': cumm_paye,
            })

        return result


class WrappedReportAureolNraReport(osv.AbstractModel):
    _name = 'report.aureol.nra_report_template'
    _inherit = 'report.abstract_report'
    _template = 'aureol.nra_report_template'
    _wrapped_report_class = AureolNraReport
