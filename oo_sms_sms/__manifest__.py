# -*- coding: utf-8 -*-
{
    'name': "Send SMS",

    'summary': """
        Sms on invoices and orders""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'license': "LGPL-3",
    'category': 'Uncategorized',
    'version': '13.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale', 'purchase'],
    'external_dependencies': {
        'python': ['africastalking']
    },
    'data': [
        'views/res_config.xml'
    ]


}
