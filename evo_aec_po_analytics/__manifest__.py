# -*- coding: utf-8 -*-
{
    'name' : 'PO Analytical Account',
    'version' : '11.1',
    'summary': 'Purchase Analytical Account Enhancement',
    'category': 'Purchase',
    'website': 'https://www.evozard.com',
    'author': 'Evozard',
    'depends' : ['analytic', 'purchase', 'account'],
    'data': [
        'views/account_analytic_account_view.xml',
        'views/account_analytic_tag_view.xml',
        'views/purchase_view.xml',
        'views/account_move_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
