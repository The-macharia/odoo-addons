# -*- coding: utf-8 -*-
{
    'name': "KCM & Staff Commission",

    'summary': """
        Create kcm invoices and sales agent invoices.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",


    'category': 'Uncategorized',
    'version': '14.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'base', 'hr_payroll'],

    # always loaded
    'data': [
        'views/account.xml',
        'views/payroll.xml',
        'views/res_models.xml',
    ],
}
