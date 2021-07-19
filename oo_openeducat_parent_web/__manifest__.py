# -*- coding: utf-8 -*-
{
    'name': "OpenEducat Parent Web",

    'summary': """
        Parents can access the route '/my/child'""",

    'description': """
        Long description of module's purpose
    """,

    'author': "The-Macharia",
    'website': "http://www.yourcompany.com",

    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website', 'openeducat_core', 'openeducat_exam', 'account', 'website_event'],

    # always loaded
    'data': [
        'report/marksheet.xml',
        'report/report.xml',

        'wizard/wizard.xml',

        'views/assets.xml',
        'views/home.xml',
        'views/home_redirects.xml',
        'views/views.xml',
        'views/op_course.xml',
    ],

}
