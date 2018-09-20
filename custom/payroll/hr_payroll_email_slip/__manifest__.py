{
    'name': 'Email Payslip',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'summary': "Adds the ability to email employee payslip",
    'author': "Francis Bangura <francisbnagura@gmail.com>, "
              "Odoo Community Association (OCA)",
    'website': 'http://odoo.com',
    'depends': ['hr_payroll', 'hr_payroll_chatter'],
    'data': [
        'views/hr_payslip_view.xml',
        'views/hr_payslip_run_view.xml',
        'data/payslip_emailtemplate.xml',
    ],
    'installable': True,
}
