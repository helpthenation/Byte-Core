# -*- coding: utf-8 -*-

{
    'name': 'Holidays Evaluation Allocation',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Computes the actual days for which employee will be on leave '
               'taking into account both rest days and public holidays',
    'author': 'Salton Massally<smassally@idtlabs.sl> '
              'Odoo Community Association (OCA)',
    'website': 'http://idtlabs.sl',
    'depends': ['hr_holidays', 'hr_holidays_legal_leave', 'hr_period',
                'hr_employee_service_length', 'hr_holidays_legal_leave'],
    'data': [
        'views/hr_holidays_status.xml',
        # 'views/hr_holidays.xml',
        'views/hr_holidays_evaluation_ruleset.xml',
        'views/hr_holidays_evaluation_rule.xml',
        'security/ir.model.access.csv',
        'data/cron.xml'
    ],
    'installable': True,
}
