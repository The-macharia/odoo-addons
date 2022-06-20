# -*- coding: utf-8 -*-
{
    'name': "Custom Reports",

    'summary': """
        customized delivery note and loading reports""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Teclea Limited",
    'website': "http://www.yourcompany.com",

    'category': 'Reports',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'reports/loading.xml',
        'reports/report.xml',
    ]
}
