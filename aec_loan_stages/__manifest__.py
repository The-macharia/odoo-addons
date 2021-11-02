#!/usr/bin/env python
# -*- encoding: utf-8 -*-

{
    'name' : 'AEC Loan Stages',
    "version" : "11.0",
    "depends" : ['pragtech_loan'],
    "author" : "Pragmatic Techsoft Pvt. Ltd.",
    "description": """Stages On Loan Application.
    """,
    "website" : "http://www.pragtech.co.in",
    "init_xml" : [],
    "data" : [
        "security/ir.model.access.csv",
        "views/aec_loan_asset.xml",
        "views/loan_stages_view.xml",
        "data/loan_default_stages.xml",
        "views/loan_view.xml",
    ],
    "active": False,
    "installable": True,
}
