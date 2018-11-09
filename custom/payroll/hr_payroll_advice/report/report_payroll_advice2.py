import time
from datetime import datetime
from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools import amount_to_text_en


class PayrollAdviceReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(PayrollAdviceReport, self).__init__(cr, uid, name,
                                                    context=context)

        self.localcontext.update({
            'get_month': self.get_month,
            'get_detail': self.get_detail,
            'get_total_sal': self.get_total_sal,
            'get_currency': self.get_currency,
            'get_signatories': self.get_signatories,

        })
        self.context = context
        self.total_bysal = 0.00


    def get_month(self, advice_id):
        date = advice_id.date_from
        date_dt = datetime.strptime(date, '%Y-%m-%d')
        return date_dt.strftime("%B").upper()+" "+str(date_dt.year)

    def get_signatories(self, advice):
        return [advice.batch_id.signatory_1, advice.batch_id.signatory_2]


    def convert(self, amount, cur):
        return amount_to_text_en.amount_to_text(amount, 'en', cur)

    def get_bysal_total(self):
        return self.total_bysal

    def get_currency(self, advice):
        return advice.currency_id

    def get_detail(self, advice):
        result = []
        for l in advice.line_ids:
            res = {}
            res.update({
                'name': l.employee_id.name,
                'acc_no': l.name,
                'bysal': l.bysal,
                'debit_credit': l.debit_credit,
            })
            self.total_bysal += l.bysal
            result.append(res)
        return result

    def get_total_sal(self, advice):
        total_bysal = 0.0
        for l in advice.line_ids:
            total_bysal += l.bysal
        return total_bysal

class WrappedReportPayrollAdviceReport(osv.AbstractModel):
    _name = 'report.hr_payroll_advice.report_payrolladvice'
    _inherit = 'report.abstract_report'
    _template = 'hr_payroll_advice.report_payrolladvice'
    _wrapped_report_class = PayrollAdviceReport


