from odoo.tests import common
from psycopg2 import IntegrityError


class TestEmployeeID(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeID, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.employee_id_model = self.env['hr.employee.personal.id']
        self.employee_id_type_model = self.env['hr.employee.personal.id.type']
        self.employee = self.employee_model.create({'name': 'Employee',
                                                    'initial_employment_date': '2015-02-09'})
        self.employee0 = self.employee_model.create({'name': 'Employee0',
                                                    'initial_employment_date': '2015-03-09'})
        self.id_type = self.employee_id_type_model.create({'name': 'Passport'})
        self.employee_id = self.employee_id_model.create({'employee_id': self.employee.id,
                                                          'id_type': self.id_type.id,
                                                          'id_number': 'E39034',
                                                          'expiry_date': '2018-01-01'})

    def test_duplicate_identification_type(self):
        with self.assertRaises(IntegrityError):
            self.employee_id_type_model.create({'name': 'Passport'})

    def test_duplicate_identification(self):
        with self.assertRaises(IntegrityError):
            self.employee_id_model.create({'employee_id': self.employee0.id,
                                           'id_type': self.id_type.id,
                                           'id_number': 'E39034',
                                           'expiry_date': '2019-01-05'})
        # with self.assertRaises(IntegrityError):
            self.employee_id_model.create({'employee_id': self.employee0.id,
                                           'id_type': self.id_type.id,
                                           'id_number': 'E390346',
                                           'expiry_date': '2018-01-05'})

