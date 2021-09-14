# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.website.controllers.main import Website


class Website(Website):

    @http.route(auth='public')
    def index(self, data={}, **kw):
        super(Website, self).index(**kw)
        return http.request.render('oo_website_booking.home', data)


class OoWebsiteBooking(http.Controller):
    @http.route('/', type='http', csrf=True, website=True, auth='public', method='GET')
    def index(self, **kw):
        return request.render('oo_website_booking.home')
