{
    'name': 'Employee End of Service Benefit',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Allows the definition of legal/annual leave',
    'author': 'Francis Bangura<francisbnagura@gmail.com>, ',
    'website': 'http://byteltd.com',
    'depends': ['hr_employee_service_length', 'hr_payroll'],
    'data': [
        'views/hr_contract_type.xml',
    ],
    'installable': True,
}
