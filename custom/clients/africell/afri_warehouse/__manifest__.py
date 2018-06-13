{
    'name': 'Africell Warehouse',
    'version': '10.0.1.0.0',
    'author': 'Francis Bangura <Byte Limited>',
    'category': 'Auto Messiah',
    'website': 'http://www.byteltd.com',
    'license': 'AGPL-3',
    'demo': [
    ],
    'depends': [
        'export_stockinfo_xls',
        'abs_warehouse_product',
        'warehouse_stock_restrictions',
    ],
    'data': [
        'data/sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/warehouse_department.xml',
        'views/warehouse_request.xml',
        'views/res_users.xml',
        'menus/menus.xml',
    ],
    'installable': True
}
