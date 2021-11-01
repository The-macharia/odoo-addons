# -*- coding: utf-8 -*-
{
    'name': "Invoice Reports",

    'summary': """
       Multi company invoice reports""",

    'description': """
        Long description of module's purpose
    """,

    'author': "@the-macharia",
    'website': "github.com/the-macharia",


    'category': 'Extra-Tools',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale'],

    # always loaded
    'data': [
        'reports/views.xml',
        'reports/templates.xml',
    ]
}
