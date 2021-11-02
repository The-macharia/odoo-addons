#!/usr/bin/env python
# -*- encoding: utf-8 -*-


{
    'name' : 'AEC Partner Extension',
    "version" : "1.0",
    "Category" : ["Tools"],
    "depends" : ["base", "contacts","sale", "pragtech_loan", "evozard_aec_customization_11c"],
    "author" : "Pragmatic Techsoft Pvt. Ltd.",
    "website" : "http://www.pragtech.co.in",
    "summary" : "Province, District, State, Sector, Cell",
    "data" : [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/import_partner_view.xml",
        "views/partner_view.xml",
        "views/training_details_view.xml",
        "views/loan_view.xml",
    ],
    "active": False,
    "installable": True,
    'images': [],
}
