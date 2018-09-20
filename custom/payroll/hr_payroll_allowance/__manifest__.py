{
    "name": "Payroll Allowance",
    "version": "1.0",
    'license': 'AGPL-3',
    "depends": ["hr_payroll", "hr_employee_service_length"],
    'author': "Francis Bangura <fbangura@byteltd.com>",
    'category': 'HR',
    "summary": "Add payroll allowance functionality",
    "data": [
        "views/hr_payroll_allowance.xml",
        'views/hr_contract.xml',
        # 'security/ir.model.access.csv',
        # 'security/ir_rule.xml'
    ],
    'installable': True,
}
