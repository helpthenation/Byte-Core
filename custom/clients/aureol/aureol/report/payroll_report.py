import time
from datetime import datetime
from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools import amount_to_text_en


class AureolPayrollReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AureolPayrollReport, self).__init__(cr, uid, name,
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
                'overtime': s.line_ids.filtered(lambda r:r.code=="OTM").total,
                'transport': s.line_ids.filtered(lambda r:r.code=="TALW").total,
                'ent': s.line_ids.filtered(lambda r:r.code=="ENT").total,
                'gross': s.line_ids.filtered(lambda r:r.code=="GROSS").total,
                'nassit': s.contract_id.wage*0.05,
                'paye': s.line_ids.filtered(lambda r: r.code == "PAYE").total,
                'advance': s.line_ids.filtered(lambda r: r.code == "SALADV").total,
                'union': s.line_ids.filtered(lambda r: r.code == "UNION").total,
                'medical': s.line_ids.filtered(lambda r: r.code == "MEDICLOAN").total,
                'insurance': s.line_ids.filtered(lambda r: r.code == "PREINS").total,
                'car': s.line_ids.filtered(lambda r: r.code == "CAR").total,
                'ded': s.line_ids.filtered(lambda r: r.code == "TOTALDED").total,
                'net': s.line_ids.filtered(lambda r: r.code == "NET").total,
            })

        return result


class WrappedReportAureolPayrollReport(osv.AbstractModel):
    _name = 'report.aureol.payroll_report_template'
    _inherit = 'report.abstract_report'
    _template = 'aureol.payroll_report_template'
    _wrapped_report_class = AureolPayrollReport
