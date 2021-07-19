# -*- coding: utf-8 -*-
{
    'name': "Remittance Report",

    'summary': """
        Remittance report.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "@the-macharia",
    'website': "sailotech.com",

    'category': 'Account',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'reports/report.xml',
        'reports/remittance.xml',
    ]
}
