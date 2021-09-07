# -*- coding: utf-8 -*-
{
    'name': "Purchase Sequence",

    'summary': """
        Purchase sequence based on import or local purchase""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Eric Waweru",
    'website': "http://www.yourcompany.com",

    'category': 'Purchase',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/views.xml',
        'data/sequence.xml',
    ]
}
