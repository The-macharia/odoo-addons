# -*- coding: utf-8 -*-
{
    'name': "Analytic Report",

    'summary': """
        Generate analytic line reports.""",

    'description': """
    """,
    'author': "@the-macharia",
    'website': "github.com/the-macharia",
    'category': 'Extra Tools',
    'version': '12.0.0.1.0',

    'depends': ['account'],
    'external_dependencies': {'python': ['openpyxl']},

    'data': [
        'wizards/wizard.xml',
        'views/menu.xml',
    ]
}
