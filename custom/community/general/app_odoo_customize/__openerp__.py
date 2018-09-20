{
    'name': 'Byte Customization',
    'version': '10.0.1.0',
    'author': 'Francis Bangura <francisbnagura@gmail.com>',
    'category': 'Productivity',
    'website': 'http://www.byteltd.com',
    'license': 'AGPL-3',
    'sequence': 2,
    'depends': ['web'],
    'data': [
        'views/app_odoo_customize_view.xml',
        'views/app_theme_config_settings_view.xml',
        'data/ir_config_parameter.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
        'static/src/xml/customize_user_menu.xml',
    ],
}

