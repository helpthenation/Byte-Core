from odoo import models, api, fields


class PayrollAdvice(models.Model):

    _inherit = 'hr.payroll.advice'
    note = fields.Text(
        'Description',
        compute='compute_note',
        store=True
    )


    @api.multi
    def compute_note(self):
        gender = ''
        name=''
        for rec in self:
            if len(rec.line_ids)==1:
                for line in rec.line_ids:
                    if line.employee_id and line.employee_id.gender=='male':
                        gender='his'
                        name = 'name'
                    if line.employee_id and line.employee_id.gender=='female':
                        gender='her'
                        name='name'
            if len(rec.line_ids)>1:
                gender='their'
                name='names'
            # lets get the note
            note = "Upon receipt of this letter, kindly credit the undermentioned Accocunt with the amount against" \
                   " " + gender + " " + name + " and Debit our Account Number 01-1031577 with the corresponding amount."
            rec.note = note

    @api.multi
    def compute_advice(self):
        """
        Advice - Create Advice lines in Payment Advice and
        compute Advice lines.
        """
        payslip_pool = self.env['hr.payslip']
        advice_line_pool = self.env['hr.payroll.advice.line']
        payslip_line_pool = self.env['hr.payslip.line']

        for advice in self:
            advice.line_ids.unlink()
            slips = self.batch_id.slip_ids.filtered(
                lambda r: r.state == 'done'
                and r.employee_id.bank_account_id
                and r.employee_id.bank_account_id.bank_id == self.bank_id
            )
            for slip in slips:
                line = payslip_line_pool.search(
                    [('slip_id', '=', slip.id), ('code', '=', 'NET')],
                    limit=1
                )
                if line and line.total>0:
                    advice_line = {
                        'advice_id': advice.id,
                        'account_id': slip.employee_id.bank_account_id.id,
                        'employee_id': slip.employee_id.id,
                        'bysal': line.total,
                        'slip_id': slip.id,
                    }
                    advice_line_pool.create(advice_line)
                    slip.advice_id = advice.id
            advice.compute_note()
        return True