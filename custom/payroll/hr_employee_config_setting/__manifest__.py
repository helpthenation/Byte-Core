# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Config Settings',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 38,
    'description': "Configuration wizard for HR settings",
    'website': 'http://byteltd.com',
    'depends': [
        'hr'
    ],
    'data': [
        'res_config_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
