{
    'name': 'Employee Leaves UPA',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Uninterrupted Personal Affairs Leave',
    'author': 'Francis Bangura<francis@byteltd.com>',
    'website': 'http://byteltd.com',
    'depends': ['hr_holidays_legal_leave', 'hr_holidays_evaluate_allocation',
                'hr_holidays_settings'],
    'data': [
        'views/hr_holidays_upa.xml',
        'views/res_config.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
