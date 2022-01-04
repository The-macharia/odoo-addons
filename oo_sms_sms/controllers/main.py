# -*- coding: utf-8 -*-
# from odoo import http


# class OoSmsSms(http.Controller):
#     @http.route('/oo_sms_sms/oo_sms_sms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oo_sms_sms/oo_sms_sms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('oo_sms_sms.listing', {
#             'root': '/oo_sms_sms/oo_sms_sms',
#             'objects': http.request.env['oo_sms_sms.oo_sms_sms'].search([]),
#         })

#     @http.route('/oo_sms_sms/oo_sms_sms/objects/<model("oo_sms_sms.oo_sms_sms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oo_sms_sms.object', {
#             'object': obj
#         })
