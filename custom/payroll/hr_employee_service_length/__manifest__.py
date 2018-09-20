{
    'name': 'Employee Service Length',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'summary': "Calculates the length of an employee's time in a company",
    'author': "Francis Bangura <fbangura@byteltd.com>, ",
    'website': 'http://byteeltd.com',
    'depends': ['hr_contract', 'hr_employee_config_setting'],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'views/hr_employee.xml',
        'views/res_company.xml',
        'views/res_config_views.xml',
    ],
    'installable': True,
}
