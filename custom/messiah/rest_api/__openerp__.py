# -*- coding: utf-8 -*-
{
    'name': 'REST API',
    'version': '1.2.2',
    'category': 'API',
    'author': 'Andrey Sinyanskiy SP',
    'support': 'avs3.ua@gmail.com',
    'license': 'Other proprietary',
    'price': 129.00,
    'currency': 'EUR',
    'summary': 'Professional RESTful API access to Odoo models with OAuth2 authentification and Redis token store',
    'shortdesc': """
This module provide professional RESTful API (json) access to Odoo models with OAuth2 authentification (very simplified) and Redis token store.
""",
    'external_dependencies': {
        'python' : ['redis'],
    },
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'data/ir_configparameter_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
