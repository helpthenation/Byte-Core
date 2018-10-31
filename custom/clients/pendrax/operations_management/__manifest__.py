# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Operations Process',
    'version': '1.0',
    'category': 'Operations',
    'sequence': 91,
    'summary': 'Pendrax Operations Process',
    'description': """Manage Pendrax Operations pipeline""",
    'website': 'https://www.byteltd.com',
    'author': 'Francis Bangura [Byte Limited]',
    'depends': [
        'pendrax_entry',
    ],
    'data': [
        'security/security.xml',
        #'security/ir.model.access.csv',
        'data/cron.xml',
        'data/sequence.xml',
        #'views/hr_recruitment_views.xml',
        #'report/hr_recruitment_report_views.xml',
        #'views/hr_recruitment_config_settings_views.xml',
        #'views/hr_recruitment_templates.xml',
        #'views/hr_department_views.xml',
        #'views/hr_job_views.xml',
        'views/web_asset_backend_template.xml',
        'views/hr_employee.xml',
        'views/client_quote.xml',
        'views/client_quote_templates.xml',
        'views/operations.xml',
        #'views/tour_views.xml',
    ],
    #'demo': ['data/hr_recruitment_demo.xml'],
    #'test': ['test/recruitment_process.yml'],
    'installable': True,
    #'auto_install': False,
    'application': True,
    'qweb': [
        "static/src/xml/guard_status.xml",
    ],
}
