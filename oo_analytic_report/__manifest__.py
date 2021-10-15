# -*- coding: utf-8 -*-
{
    'name': "Analytic Account Report",

    'summary': """
        Excel reports of analytic income and expense""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Extra-Tools',
    'version': '12.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'sale', 'account', 'stock'],

    # always loaded
    'data': [
        'views/views.xml',
        'wizard/wizard.xml',
        'views/menu.xml',
    ]
}
