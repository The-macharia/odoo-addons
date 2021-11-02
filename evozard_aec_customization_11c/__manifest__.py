# -*- coding: utf-8 -*-
{
    'name': 'Evozard AEC Customization',
    'category': 'Account',
    'description':"""
    Evozard AEC Customization
""",
    'author': 'Evozard',
    'website': 'https://www.evozard.com/',
    'version': '11.0.0',
    'depends': ['base', 'sale', 'account', 'project'],
    'data' : [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/invoice_view.xml',
        'views/sale_view.xml',
        'views/project_view.xml',
    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
