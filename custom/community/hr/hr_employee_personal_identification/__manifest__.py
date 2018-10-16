{
    'name': 'Employee Personal Identification',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_employee_id_type_views.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
