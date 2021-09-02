# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class OoWebsiteBooking(http.Controller):
    @http.route('/home', type='http', csrf=True, website=True, auth='public', method='GET')
    def index(self, **kw):
        return request.render('oo_website_booking.home')
