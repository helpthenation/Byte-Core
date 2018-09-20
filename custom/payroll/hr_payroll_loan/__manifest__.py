{
    "name": "Employee Loan Management",
    "version": "1.0",
    "depends": ["hr_payroll",
                "hr_payslip_amendment",
                "hr_employee_endofservice_benefit"],
    "author": "Francis Bangura<fbangura@byteltd.com>",
    'category': 'Human Resources',
    "summary": """Employee Loan Management
    """,
    "data": [
        "views/menu.xml",
        "views/hr_payroll_loan_type.xml",
        "views/hr_payroll_loan.xml",
        "views/hr_employee.xml",
        #         "views/hr_payslip_run_view.xml",
        #'security/ir.model.access.csv',
        'data/hr_payroll_loan_sequence.xml',
        'views/report_payslip.xml',
        'views/report_payslipdetails.xml'

    ],
    'installable': True,
}
