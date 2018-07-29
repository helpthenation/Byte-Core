from odoo import models, fields, api
from tempfile import NamedTemporaryFile
import csv
from odoo.exceptions import ValidationError
import datetime


class WizardGetRecord(models.TransientModel):
    
    _name = 'wizard.employee.update'
    _description = 'Update Employees'
    file = fields.Binary('CSV File', required=True)

    @api.multi
    def update_employees(self):
        self.ensure_one()
        employee_obj = self.env['hr.employee']
        data = self.file.decode('base64')
        with NamedTemporaryFile(mode='r+b') as tempInFile:
            tempInFile.write(data)
            tempInFile.seek(0)
            del data
            rows = csv.DictReader(tempInFile.file, delimiter=',', quotechar='"')
            if 'DB ID' not in rows.fieldnames:
                raise ValidationError('Error Required field DB ID not available')
            for row in rows:
                db_id = row['DB ID']
                new_id = row['NEW ID']
                old_id = row['OLD ID']
                if new_id != old_id:
                    emp = employee_obj.search([('id', '=', db_id)])
                    emp.write({'empid': new_id,
                               'empid2': new_id
                               })
        return True
