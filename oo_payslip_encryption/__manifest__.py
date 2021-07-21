# -*- coding: utf-8 -*-
{
    'name': "Payslip Encryption",
    'version': '1',

    'description': """Send encrypted payslips via email to employees

    """,
    'summary': "Send encrypted payslips via email to employees",


    'author': "@the-macharia",
    'website': "github.com",
    'license': 'LGPL-3',

    'category': 'Extra Tools',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],
    'data': ['views/views.xml']
}
