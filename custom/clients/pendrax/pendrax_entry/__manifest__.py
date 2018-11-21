{
    'name': 'Pendrax Data Entry',
    'version': '10.0.1.0.0',
    'author': 'Francis Bangura <Byte Limited>',
    'category': 'Utility',
    'website': 'http://www.byteltd.com',
    'license': 'AGPL-3',
    'demo': [
    ],
    'depends': [
        'hr_employee_name_split','hr_payroll_loan'
    ],
    'data': [
        'security/security.xml',
        'views/hr_employee.xml',
        'views/occupation.xml',
        'views/qualification.xml',
        'views/district.xml',
        'views/province.xml',
        'views/tribe.xml',
        'views/area.xml',
        'views/area.xml',
        'views/res_company.xml',
        'views/hr_loan_view.xml',
        'views/hr_holidays_view.xml',
        'report/approval_reports.xml',
        'report/approval_templates.xml',
        'views/religion.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
