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
            'get_detail':self.get_detail,

        })
        self.context = context
    def get_header_text(self, run_id):
        date = run_id.date_payment
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return "CONTRIBUTION SCHEDULE FOR THE MONTH OF " +date_dt.strftime("%B").upper()+", "+str(date_dt.year)


    def get_month(self, run_id):
        date = run_id.date_payment
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return date_dt.strftime("%B").upper()


    def convert(self, amount, cur):
        return amount_to_text_en.amount_to_text(amount, 'en', cur)

    def get_detail(self, slip_ids):
        result = []
        for s in slip_ids:
            result.append({
                'er': s.employee_id.er_number or "",
                'est_name': "AUREOL INSURANCE CO. LTD",
                'ssnid': s.employee_id.ssnid or "",
                'lname': s.employee_id.lname or "",
                'fname': s.employee_id.fname or "",
                'mname': s.employee_id.mname or "",
                'salary': s.employee_id.contract_id.wage,
                'total': s.employee_id.contract_id.wage*0.15,
            })

        return result


class WrappedReportAureolNraReport(osv.AbstractModel):
    _name = 'report.aureol.nassit_report_template'
    _inherit = 'report.abstract_report'
    _template = 'aureol.nassit_report_template'
    _wrapped_report_class = AureolNraReport
