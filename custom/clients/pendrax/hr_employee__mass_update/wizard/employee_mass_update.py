from odoo import models, fields, api
from tempfile import NamedTemporaryFile
import csv
from odoo.exceptions import ValidationError
import logging
import os
import base64
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


class WizardGetRecord(models.TransientModel):
    
    _name = 'wizard.employee.update'
    _description = 'Update Employees'
    file = fields.Binary('CSV File')
    date = fields.Date(string='Date')
    dest_dir = fields.Char("Image Directory")

    @api.multi
    def name_id_valid(self):
        for rec in self.env['hr.employee'].search([]):
            rec.compute_name_id()

    @api.multi
    def correct_names(self):
        self.ensure_one()
        employee_object = self.env['hr.employee'].search([])
        for employee in employee_object:
            f = '';
            m = '';
            l = '';
            name=employee.name.split(' ')
            f=name[0]
            l=name[-1]
            try:
                name.pop(0)
            except Exception:
                pass
            try:
                name.pop(-1)
            except Exception:
                pass
            for n in name:
                m+=n
            employee.fname=f
            employee.mname=m
            employee.lname=l



    @api.multi
    def set_guard(self):
        employee_object = self.env['hr.employee'].search([])
        self.ensure_one()
        for employee in employee_object:
            if employee.job_id.guard_position:
                employee.is_guard=True




    @api.multi
    def purgebankacc(self):
        payslip_obj = self.env['hr.payslip.run']
        for run in payslip_obj.search([]):
            for slip in run.slip_ids:
                slip.write({'state': 'draft'})
        return True

    @api.multi
    def fix_employee_job(self):
        cos=self.env['hr.contract'].search([])
        for con in cos:
            con.employee_id.job_id = con.job_id


    @api.multi
    def empEmpDate(self):
        contract_obj = self.env['hr.contract']
        eontracts = contract_obj.search([])
        a = 0
        b = 50
        for counter in range(1, (len(eontracts) / 50) + 1):
            for contract in eontracts[a:b]:
                contract.date_start = contract.employee_id.emp_date and contract.employee_id.emp_date or "2001-01-01"
                contract.employee_id.initial_employment_date = contract.employee_id.emp_date and contract.employee_id.emp_date or "2001-01-01"

                if contract.date_start>contract.employee_id.initial_employment_date:
                    contract.date_start = contract.employee_id.emp_date or "2001-01-01"
                    contract.initial_employment_date = contract.employee_id.emp_date or "2001-01-01"

                else:
                    contract.employee_id.initial_employment_date = contract.employee_id.emp_date or "2001-01-01"
                    pass
                contract.trial_date_end = fields.Date.from_string(contract.employee_id.emp_date and contract.employee_id.emp_date or "2001-01-01") + relativedelta(months=+6)
                #trial_date_start, trial_date_end
            a += 50
            b += 50
        return True

    @api.multi
    def purgedupcon(self):
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        for emp in employee_obj.search([]):
            cons=contract_obj.search([('employee_id', '=', emp.id)])
            if len(cons)>1:
                in_list=[con for con in cons]
                in_list.sort
                in_list[0].unlink()
        return True

    @api.multi
    def update_admin_employees(self):
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
                nassit = row['NASSIT']
                name = row['NAME']
                absent = row['ABS']
                med_allowance = row['MALW']
                rent_allw = row['RALW']
                ecta_allw = row['ECTA']
                tp_allw = row['TALW']
                gen_allw = row['GENALW']
                staff_cat = row['CAT']
                sal_structure = row['STRUC']
                employee = employee_obj.search([('empid', '=', emp_id)])
                # lets fix staff category
                if employee and employee.empid:

                    employee.nassit_no = nassit
                    employee.name = name
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
                                                        'wage': wage,
                                                        'struct_id': sal_structure,
                                                        'date_start': employee.emp_date

                                                    }
                    _logger.info("Creating contract for %s"%employee.name)
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
                    absen_lines = []
                    if len(absent) > 1:
                        absen_lines.append((0, 0, {
                            'employee_id': employee.id,
                            'date': self.date and self.date,
                            'days': absent,
                            'reason_id': 1}))
                    employee.write({
                        'absent_ids': absen_lines
                    })
                    _logger.info("Updated records for %s" % employee.name)

        return True

    @api.multi
    def update_guard_employees(self):
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
                wage = row['WAGE']
                location = row['LOC']
                absent = row['ABS']
                gen_allw = row['GENALW']
                staff_cat = row['CAT']
                sal_structure = row['STRUC']
                employees = employee_obj.search([('empid', '=', emp_id)])
                # lets fix staff category
                if employees:
                    for employee in employees:
                        employee.bank_account_id.unlink()
                        employee.staff_category = staff_cat
                        employee.staff_location = location
                        # lets first create bank accounts
                        # delete duplicate account

                        # Lets Create Contract
                        datas = {'name': employee.name+"("+employee.empid+")",
                                                            'employee_id': employee.id,
                                                            'type_id': 19,
                                                            'job_id': employee.job_id.id,
                                                            'wage': float(wage),
                                                            'struct_id': int(sal_structure),
                                                            'date_start': employee.emp_date and employee.emp_date or '2018-05-05'

                                                        }
                        contract = contract_obj.create(datas)
                        # lets create allowance
                        allowance_lines = []
                        if len(gen_allw) > 1:
                            allowance_lines.append((0, 0, {
                                'contract_id': contract.id,
                                'amount': float(gen_allw),
                                'allowance_id': allowance_obj.search([('code', '=', 'GENALW')]).id}))
                        contract.write({'allowance_line_ids': allowance_lines})
                        absen_lines = []
                        if len(absent) > 1:
                            absen_lines.append((0, 0, {
                                'employee_id': employee.id,
                                'date': self.date and self.date,
                                'days': absent,
                                'reason_id': 1}))
                        employee.write({
                            'absent_ids': absen_lines
                        })
                        _logger.info("Updated records for %s" % employee.name)

        return True

    @api.multi
    def create_employees(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']

        data = self.file.decode('base64')
        with NamedTemporaryFile(mode='r+b') as tempInFile:
            tempInFile.write(data)
            tempInFile.seek(0)
            del data
            rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
            if 'ID' not in rows.fieldnames:
                raise ValidationError('Error Required field EMP ID not available')
            created=0
            for row in rows:
                emp_id = row['ID']
                emp_name = row['NAME']
                cat = row['CAT']
                loc = row['LOC']
                phone = row['PHONE']
                employee_obj.create({'name': emp_name,
                                     'empid': emp_id,
                                     'empid2': emp_id,
                                     'phone': phone,
                                     'staff_category': cat,
                                     'staff_location': loc,
                                     'date_of_birth': '2018-01-01',
                                     'incomplete_info': True
                                     })
                created += 1
                # lets fix staff category
                _logger.info("Created %s Employees for" % created)

        return True

    @api.multi
    def update_bank_accounts(self):
        self.ensure_one()
        employee_object = self.env['hr.employee']

        data = self.file.decode('base64')
        with NamedTemporaryFile(mode='r+b') as tempInFile:
            tempInFile.write(data)
            tempInFile.seek(0)
            del data
            rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
            if 'ID' not in rows.fieldnames:
                raise ValidationError('Error Required field EMP ID not available')
            for row in rows:
                eid = str(row['ID'])
                name = str(row['NAME'])
                account = str(row['ACCOUNT'])
                bank = str(row['BANK'])
                if len(eid)>1:
                    employee = employee_object.search([('empid', '=', eid)])
                    employee.name=name
                    employee.compute_name_id
                    employee.bank_account_id.bank_id = bank
                    employee.bank_account_id.acc_number = account
        return True

    @api.multi
    def create_bank_accounts(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']
        emp_bank_obj = self.env['res.partner.bank']
        for rec in self:
            data = rec.file.decode('base64')
            with NamedTemporaryFile(mode='r+b') as tempInFile:
                tempInFile.write(data)
                tempInFile.seek(0)
                del data
                rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
                if 'ID' not in rows.fieldnames:
                    raise ValidationError('Error Required field EMP ID not available')
                new_accounts=[]
                for row in rows:
                    bank = str(row['BANK'])
                    account = str(row['ACCOUNT'])
                    emp_id = str(row['ID'])
                    new_accounts.append(account)
                    employee = employee_obj.search(([('empid', '=', emp_id)]))
                    if not employee.bank_account_id.id:
                        account = emp_bank_obj.create({'acc_number': account,
                                                       'bank_id': bank})
                        employee.bank_account_id = account.id
    
            return True

    @api.multi
    def create_paye_adjustment(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']
        for rec in self:
            data = rec.file.decode('base64')
            with NamedTemporaryFile(mode='r+b') as tempInFile:
                tempInFile.write(data)
                tempInFile.seek(0)
                del data
                rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
                if 'ID' not in rows.fieldnames:
                    raise ValidationError('Error Required field EMP ID not available')
                for row in rows:
                    amount = str(row['AMOUNT'])
                    emp_id = str(row['ID'])
                    employee = employee_obj.search(([('empid', '=', emp_id)]))
                    if employee.contract_id:
                        employee.contract_id.paye_adjustment=amount
            return True

    @api.multi
    def inactivate(self):
        self.ensure_one()
        employee_object = self.env['hr.employee']
        e_list = employee_object.search([])
        for employee in e_list:
            _logger.info("Checking %s"%employee.name)
            if len(employee.contract_ids)<1:
                employee.active = False
        return True

    @api.multi
    def create_guard_loan(self):
        ammendment_obj=self.env['hr.payslip.amendment']
        employee_obj = self.env['hr.employee']
        for rec in self:
            data = rec.file.decode('base64')
            with NamedTemporaryFile(mode='r+b') as tempInFile:
                tempInFile.write(data)
                tempInFile.seek(0)
                del data
                rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
                if 'ID' not in rows.fieldnames:
                    raise ValidationError('Error Required field EMP ID not available')
                for row in rows:
                    comment = str(row['COMMENT'])
                    emp_id = str(row['ID'])
                    amount = str(row['LOAN'])
                    employee = employee_obj.search([('empid','=',emp_id)])
                    ammendment = ammendment_obj.search([('employee_id', '=', employee.id)])
                    if ammendment.amount==int(amount):
                        ammendment.note=comment

    @api.multi
    def create_location_date(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']
        for rec in self:
            data = rec.file.decode('base64')
            with NamedTemporaryFile(mode='r+b') as tempInFile:
                tempInFile.write(data)
                tempInFile.seek(0)
                del data
                rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
                if 'ID' not in rows.fieldnames:
                    raise ValidationError('Error Required field EMP ID not available')
                for row in rows:
                    name = str(row['NAME'])
                    loc = str(row['LOCATION'])
                    date = str(row['DATE'])
                    emp_id = str(row['ID'])
                    employee = employee_obj.search(([('empid', '=', emp_id)]))
                    employee.deployment = loc
                    employee.name = name
                    employee.compute_name_id()
                    if len(date) > 1:
                        employee.emp_date = date
            return True

    @api.multi
    def update_abs(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']
        for rec in self:
            data = rec.file.decode('base64')
            with NamedTemporaryFile(mode='r+b') as tempInFile:
                tempInFile.write(data)
                tempInFile.seek(0)
                del data
                rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
                if 'ID' not in rows.fieldnames:
                    raise ValidationError('Error Required field EMP ID not available')
                for row in rows:
                    absent = str(row['ABS'])
                    emp_id = str(row['ID'])
                    location = str(row['LOC'])
                    name = str(row['NAME'])
                    employee = employee_obj.search(([('empid', '=', emp_id)]))
                    employee.name=name
                    employee.compute_name_id
                    employee.deployment=location
                    if len(employee.absent_ids) < 1:
                        absen_lines = []
                        if len(absent) >= 1 and int(absent) >= 1:
                            absen_lines.append((0, 0, {
                                'employee_id': employee.id,
                                'date': self.date and self.date,
                                'days': absent,
                                'reason_id': 1}))
                        if len(absen_lines) >= 1:
                            employee.write({
                                'absent_ids': absen_lines
                            })
            return True
    @api.multi
    def add_photos(self):
        missing=[]
        destdir = self.dest_dir
        files = [f for f in os.listdir(destdir) if os.path.isfile(os.path.join(destdir, f))]
        '''
        employees=self.env['hr.employee'].search([])
        x=0
        y=50
        for count in range(1,(len(employees)/50)+1):
            for em in employees[x:y]:
                em.image=False
            x+=50
            y+=50
        '''
        a = 0
        b = 50
        for counter in range(1,(len(files)/50)+1):
            for image in files[a:b]:
                with open(destdir+image, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                    lookup_id =image.split(".")[0]
                    employee = self.env['hr.employee'].search([('empid', '=', lookup_id)])
                    if len(employee)==1 and not employee.image:
                        employee.image = encoded_string
                    elif not employee:
                        missing.append(lookup_id)

            a += 50
            b += 50
        print missing



