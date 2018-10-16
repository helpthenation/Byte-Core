{
    "name": "Employee Contract History",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    "category": "Human Resources",
    "summary": "manage employee contract history",
    "depends": [
        'hr_contract'
    ],
    "data": [
        'views/hr_contract_view.xml',
        'data/hr_contract_cron.xml',
    ],
    'installable': True,
}
