# -*- coding: utf-8 -*-
{
    'name': "Payslip Template",

    'summary': """
        Customized Payslip Template.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "@the-macharia",
    'website': "http://www.yourcompany.com",


    'category': 'Employees',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],

    # always loaded
    'data': [
        'reports/report.xml',
        'reports/payslip.xml',
    ]
}
