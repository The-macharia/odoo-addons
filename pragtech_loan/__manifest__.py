#!/usr/bin/env python
# -*- encoding: utf-8 -*-


{
    'name': 'Loan Management',
    "version": "1.1",
    "depends": ["base", "account", "sale_coupon", 'web_domain_field'],
    "author": "Pragmatic Techsoft Pvt. Ltd.",
    "description": """Loan Management System
    * Integrated to Accounting System
    * Usefull for any type of Loans - Home, Business, Personal
    * Clean Varification Process for Proofs
    * Workflow for Loan Approval/Rejection
    * Reports related to the Loans, Documents, Loan Papers
    * Dynamic Interest Rates Calculation
    """,
    "website": "http://www.pragtech.co.in",
    "init_xml": [],
    "demo": [
        #         "demo/loan_demo.xml"
    ],
    "data": [
        "security/loan_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/loan_classifications_data.xml",
        "report/loan_report_view.xml",
        "wizard/loan_extended_view.xml",
        "views/loan_asset.xml",
        "views/loan_payment_view.xml",
        "wizard/payment_schedule_view.xml",
        "wizard/payment_receipt_wizard.xml",
        "views/res_users_view.xml",
        "views/loan_view.xml",
        "views/loan_dashboard.xml",
        "views/loantype_view.xml",
        "views/loan_sequence.xml",
        "views/loan_report.xml",
        "views/loan_scheduler.xml",
        "views/classifications_view.xml",
        "wizard/disbursement_wizard_view.xml",
        "report/payment_receipt_report_view.xml",
        "report/loan_info.xml",
        "report/merge_letter.xml",
        "views/res_config_settings_views.xml",


        #         "views/loan_workflow.xml",
        #         "views/loan_wizard.xml",
        #         "views/cheque_workflow.xml",

    ],
    'price': 1000,
    'currency': 'EUR',
    "active": False,
    "installable": True,
    'images': ['images/main_screenshot.png'],
}
