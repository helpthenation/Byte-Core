{
    'name': 'HR Holidays Legal Leave',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Allows the definition of legal/annual leave',
    'author': 'Francis Bangura<francis@byteltd.com>, '
              'Odoo Community Association (OCA)',
    'website': 'http://byteltd.com',
    'depends': ['hr_holidays', 'hr_holidays_settings'],
    'data': [
        'views/res_company.xml',
        'views/res_config.xml'
    ],
    'installable': True,
}
