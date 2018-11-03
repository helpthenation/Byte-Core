import time
from datetime import datetime
from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools import amount_to_text_en


class PayrollReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PayrollReport, self).__init__(cr, uid, name,
                                                    context=context)

        self.localcontext.update({
            'time': time,
            'get_month':self.get_month,
            'get_detail':self.get_detail,

        })
        self.context = context
    def get_month(self, run_id):
        date = run_id.date_payment
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return "STAFF PAYROLL FOR " +date_dt.strftime("%B").upper()+", "+str(date_dt.year)

    def convert(self, amount, cur):
        return amount_to_text_en.amount_to_text(amount, 'en', cur)

    def get_detail(self, slip_ids):
        result = []
        for s in slip_ids:
            result.append({
                'name': s.employee_id.name,
                'basic': s.contract_id.wage,
                'gross': s.line_ids.filtered(lambda r:r.code=="GROSS").total,
                'nassit': s.contract_id.wage*0.05,
                'nassitte': s.contract_id.wage*0.10,
                'paye': s.line_ids.filtered(lambda r: r.code == "PAYE").total,
                'ded': s.line_ids.filtered(lambda r: r.code == "TOTALDED").total,
                'net': s.line_ids.filtered(lambda r: r.code == "NET").total,
            })

        return result


class WrappedReportPayroll(osv.AbstractModel):
    _name = 'report.hr_payroll.payroll_report_template'
    _inherit = 'report.abstract_report'
    _template = 'hr_payroll.payroll_report_template'
    _wrapped_report_class = PayrollReport
