# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Employee Exit and Entry Process',
    'category': 'HR',
    'description': 'Employee Exit and Entry Process',

    'depends': ['base', 'stock', 'account',
                'hr_payroll', 'hr', 
                'hr_contract', 
                ],
    'data': [
        
        # Employee Checklist
        'views/checklist_setting_view.xml',
        'wizard/product_allocation_wiz_view.xml',
        'views/employee_document_view.xml',
        'views/employee_product_line_view.xml',
        'views/employee_entry_view.xml',
        'wizard/entry_product_wiz_view.xml',
        'views/employee_exit_view.xml',
        'wizard/disburse_amt_wiz_view.xml',
        'wizard/reason_cancel_view.xml',
        'wizard/exit_review_view.xml',
        'views/hr_employee_view.xml',
        'views/employee_checklist_data.xml',
        'views/stock_picking_view.xml',
        'views/employee_checklist_template.xml',
        'views/calendar_views.xml',
        'views/create_employee_view.xml',
        'security/ir.model.access.csv',
        
    ],
    
    'external_dependencies': {
        'python': [
            'numpy'
        ],
    },
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
