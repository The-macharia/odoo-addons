# -*- coding: utf-8 -*-
{
    'name': "Payments Equity",

    'summary': """
        Recieves payments made to equity and reconciles partner invoices with them""",

    'description': """
        Recieves payments made to equity and reconciles partner invoices with them
    """,

    'author': "Techlea Ltd",
    'category': 'Accounting/Payment Acquirers',
    'version': '0.1',

    'depends': ['base', 'payment', 'account', 'mail'],

    'external_dependencies': {
        'python': ['xmltodict']
    },

    'data': [
        'security/ir.model.access.csv',
        'data/payment_acquirer_data.xml',
        'data/payment_transaction_request_data.xml',
        'views/payment_acquirer_views.xml',
        'views/payment_transaction_views.xml',
        'views/payment_transaction_request_views.xml'
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
}
