from odoo import models, fields, api
from tempfile import NamedTemporaryFile
import csv
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class WizardGetRecord(models.TransientModel):
    
    _name = 'wizard.employee.update'
    _description = 'Update Employees'
    file = fields.Binary('CSV File', required=True)

    @api.multi
    def purgebankacc(self):
        employee_obj = self.env['hr.employee']
        for con in employee_obj.search([]):
            if not con.date_of_birth:
                con.date_of_birth='2010-01-01'
            con._compute_age()
        return True

    @api.multi
    def update_employees(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        emp_bank_obj = self.env['res.partner.bank']
        allowance_line_obj = self.env['hr.payroll.allowance.line']
        allowance_obj = self.env['hr.payroll.allowance']

        data = self.file.decode('base64')
        with NamedTemporaryFile(mode='r+b') as tempInFile:
            tempInFile.write(data)
            tempInFile.seek(0)
            del data
            rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
            if 'ID' not in rows.fieldnames:
                raise ValidationError('Error Required field EMP ID not available')
            for row in rows:
                emp_id = row['ID']
                bank_id = row['BANK']
                account_no = row['ACCOUNT']
                wage = row['WAGE']
                med_allowance = row['MALW']
                rent_allw = row['RALW']
                ecta_allw = row['ECTA']
                tp_allw = row['TALW']
                gen_allw = row['GENALW']
                staff_cat = row['CAT']
                sal_structure = row['STRUC']
                employee = employee_obj.search([('empid', '=', emp_id)])
                # lets fix staff category
                if employee:

                    employee.staff_category = staff_cat
                    # lets first create bank accounts
                    if not employee.bank_account_id.id:
                        account = emp_bank_obj.create({'acc_number': account_no,
                                                       'bank_id': bank_id})
                        employee.bank_account_id = account.id

                    # Lets Create Contract
                    datas = {'name': employee.name+"("+employee.empid+")",
                                                        'employee_id': employee.id,
                                                        'type_id': 19,
                                                        'job_id': employee.job_id.id,
                                                        'wage': float(wage),
                                                        'struct_id': int(sal_structure),
                                                        'date_start': employee.emp_date

                                                    }
                    contract = contract_obj.create(datas)
                    # lets create allowance
                    allowance_lines = []
                    if len(med_allowance) > 1:
                        allowance_lines.append((0, 0, {
                            'contract_id': contract.id,
                            'amount': float(med_allowance),
                            'allowance_id': allowance_obj.search([('code', '=', 'MALW')]).id}))
                    if len(rent_allw) > 1:
                        allowance_lines.append((0, 0, {
                            'contract_id': contract.id,
                            'amount': float(rent_allw),
                            'allowance_id': allowance_obj.search([('code', '=', 'RALW')]).id}))
                    if len(ecta_allw) > 1:
                        allowance_lines.append((0, 0, {
                            'contract_id': contract.id,
                            'amount': float(ecta_allw),
                            'allowance_id': allowance_obj.search([('code', '=', 'ECTA')]).id}))
                    if len(tp_allw) > 1:
                        allowance_lines.append((0, 0, {
                            'contract_id': contract.id,
                            'amount': float(tp_allw),
                            'allowance_id': allowance_obj.search([('code', '=', 'TALW')]).id}))
                    if len(gen_allw) > 1:
                        allowance_lines.append((0, 0, {
                            'contract_id': contract.id,
                            'amount': float(gen_allw),
                            'allowance_id': allowance_obj.search([('code', '=', 'GENALW')]).id}))
                    contract.write({'allowance_line_ids': allowance_lines})
                    _logger.info("Updated records for %s" % employee.name)

        return True
