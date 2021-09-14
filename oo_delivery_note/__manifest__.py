# -*- coding: utf-8 -*-
{
    'name': "Delivery Note",

    'summary': """
        Custom delivery note""",

    'description': """
    """,

    'author': "the-macharia",
    'website': "http://www.github.com/the-macharia",


    'category': 'Stock',
    'version': '14.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'sale', 'account'],

    # always loaded
    'data': [
        'reports/report.xml',
        'reports/delivery.xml',
        'reports/sale.xml',
        'reports/invoice.xml',
    ],

}
