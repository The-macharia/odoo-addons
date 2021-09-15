# -*- coding: utf-8 -*-
{
    'name': "Website Booking",

    'summary': """
        Hotel website booking""",

    'description': """
        Long description of module's purpose
    """,

    'author': "@the-macharia",
    'website': "http://www.github.com/the-macharia",

    'category': 'Website',
    'version': '12.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['website', 'hotel'],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/menus.xml',
        'views/nav.xml',
        'views/home.xml',

        'views/views.xml',
    ]
}
