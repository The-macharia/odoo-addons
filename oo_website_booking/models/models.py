# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Hotel(models.Model):
    _inherit = 'hotel.room.type'

    price = fields.Monetary(string='Price/ Night', required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True)
    currency_symbol = fields.Char(
        related='currency_id.symbol', string='Currency Symbol')
    image = fields.Binary(string='Image')
