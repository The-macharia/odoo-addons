# -*- coding: utf-8 -*-
{
    'name': "Loyalty and Savings",

    'summary': """
        Module to manage loyalty and savings""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Eric Macharia",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '15.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale_management', 'sale'],
    'external_dependencies': {'python': ['openpyxl']},

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard.xml',
        'wizards/sale_by_date.xml',
        'reports/invoice.xml',
        'reports/reports.xml',

        'views/views.xml',
        'views/loyalty.xml',
        'views/savings.xml',
        'views/stock_crates.xml',
        'views/menu.xml',
    ],
    'application': True,
}
