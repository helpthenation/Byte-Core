{
    'name': 'Auto Messiah',
    'version': '10.0.1.0.0',
    'author': 'Francis Bangura <Byte Limited>',
    'category': 'Auto Messiah',
    'website': 'http://www.byteltd.com',
    'license': 'AGPL-3',
    'demo': [
    ],
    'depends': [
        'base',
        'mail',
        'auto_messiah_settings',
        'rest_api',
        'web_map',
    ],
    'data': [
        'views/auto_vehicle_brand.xml',
        'views/auto_vehicle_model.xml',
        'views/auto_mechanic.xml',
        'views/auto_payment.xml',
        'views/auto_service.xml',
        'views/auto_towing.xml',
        'views/auto_service_type.xml',
        'views/auto_towing_resource.xml',
        'views/auto_user.xml',
        'menus/menu.xml',
        'data/auto_sequence.xml',
    ],
    'installable': True
}
