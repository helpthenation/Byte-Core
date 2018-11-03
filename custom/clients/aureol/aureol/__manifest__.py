{
    'name': 'Aureol Customization',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Aureol Customization',
    'author': 'Francis Bangura<francis@byteltd.com>',
    'website': 'http://byteltd.com',
    'depends': ['hr_payroll_allowance','web_responsive','hr_tools_aureol','hr_payroll_email_slip','hr_payroll_advice','hr_employee_name_split'],
    'data': [
            'views/hr_employee.xml',
            'report/reports.xml',
            'report/nassit_report_template.xml',
            'report/nra_report_template.xml',
            ],
    'installable': True,
}
