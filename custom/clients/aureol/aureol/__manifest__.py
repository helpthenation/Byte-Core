{
    'name': 'Aureol Customization',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Aureol Customization',
    'author': 'Francis Bangura<francis@byteltd.com>',
    'website': 'http://byteltd.com',
    'depends': ['hr_payroll_allowance',
                'web_responsive',
                'hr_tools_aureol',
                'hr_payroll_email_slip',
                'hr_payroll_advice',
                'hr_employee_name_split',
                'hr_contract_reference',
                'hr_employee_bank',
                'hr_employee_onboarding'],
    'data': [
            'views/hr_employee.xml',
            'views/hr_payslip_run.xml',
            'report/reports.xml',
            'report/nassit_report_template.xml',
            'report/nra_report_template.xml',
            'report/payroll_report_template.xml',
            'security/security.xml'

            ],
    'installable': True,
}
