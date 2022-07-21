# -*- coding: utf-8 -*-
{
    'name': "Kiosk Mrp",

    'summary': """ """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Teclea Ltd",
    'website': "http://www.yourcompany.com",


    'category': 'Uncategorized',
    'version': '15.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/views.xml',
        'views/kiosk_groups.xml',
        'views/kiosk_mrp.xml',
    ]
}
