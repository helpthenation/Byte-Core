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
        'data/cron.xml',
        'data/sequence.xml',
        'views/web_asset_backend_template.xml',
        'views/hr_employee.xml',
        'views/client_quote.xml',
        'views/client_quote_templates.xml',
        'views/operations.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
        "static/src/xml/guard_status.xml",
    ],
}
