{
    'name': 'Payslip Run Botton',
    'version': '1.0',
    'category': 'Human Resources',
    'author': "Odoo Community Association (OCA)",
    'website': 'http://odoo.com',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [

        'views/hr_payslip_run.xml',
    ],
    'installable': True,
}
