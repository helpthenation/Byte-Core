# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU AGPL as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Employment Onboarding',
    'version': '10.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Employee's Employment Status
============================

Track the HR status of employees.
    """,
    'author': 'Michael Telahun Makonnen>',
    'depends': [
        'hr_payroll', 'hr_employment_termination'
    ],
    'data': [
        'views/hr_view.xml',
    ],
    'installable': True,
}