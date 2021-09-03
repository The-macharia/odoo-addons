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
    'depends': ['stock'],

    # always loaded
    'data': [
        'reports/report.xml',
        'reports/template.xml',
    ],

}
