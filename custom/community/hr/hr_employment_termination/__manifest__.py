{
    'name': 'Employment Termination',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'summary': "Adds the ability to terminate employees",
    'depends': [
        'hr_contract', 'mail_cc_group', 'hr_employee_contract_history'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/end_employment_view.xml',
        'data/hr_employee_data.xml',
        'data/cron.xml',
        'views/hr_employee.xml',
        'views/hr_employee_termination.xml',
        'views/hr_employee_termination_reason.xml',
        'data/email_template.xml',
    ],
}
