# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from datetime import date
import logging
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)
today = date.today()


class LoyaltySavings(http.Controller):

    def _process_partner_id(self, name):
        partner_model = request.env['res.partner'].sudo()
        partner_id = partner_model.search([('name', '=', name), ('company_type', '=', 'company')], limit=1)
        if not partner_id:
            partner_id = partner_model.create({
                'name': name,
                'company_type': 'company',
                'property_account_receivable_id': 26,
                'property_account_payable_id': 51
            })
        return partner_id

    def _process_loyalty(self, partner_id, group, points):
        loyalty_model = request.env['loyalty.loyalty'].sudo()

        loyalty_id = loyalty_model.search([('partner_id', '=', partner_id.id), ('group_id', '=', group.id)], limit=1)
        line = {
            'date': today,
            'points': points,
            'collection_type': 'loyalty',
            'amount_total': float_round(group.amount_for_point * points, precision_rounding=0.01),
            'points_worth': float_round(points / group.currency_points, precision_rounding=0.01),
        }
        if not loyalty_id:
            loyalty_id = loyalty_model.create({
                'partner_id': partner_id.id,
                'group_id': group.id,
                'date_enrolled': today,
                'loyalty_lines': [(0, 0, line)]
            })
        else:
            loyalty_id.write({'loyalty_lines': [(0, 0, line)]})

    def _process_savings(self, partner_id, group, points):
        savings_model = request.env['savings.savings'].sudo()

        savings_id = savings_model.search([('partner_id', '=', partner_id.id), ('group_id', '=', group.id)], limit=1)

        line = {
            'date': today,
            'amount': points,
            'collection_type': 'savings',
        }
        if not savings_id:
            savings_id = savings_model.create({
                'partner_id': partner_id.id,
                'group_id': group.id,
                'date_enrolled': today,
                'saving_lines': [(0, 0, line)]
            })
        else:
            savings_id.write({'savings_lines': [(0, 0, line)]})

    @http.route('/loyalty/upload', type="json", csrf="None", auth="public", methods=['GET', 'POST'])
    def loyalty(self, **kw):
        group_model = request.env['loyalty.group'].sudo()

        data = json.loads(request.httprequest.get_data()).get('payload')
        for group in data:
            loyalty_group = group_model.search([('name', '=', group.strip())], limit=1)
            if not group:
                return f'Missing group {group}'
            for line in data[group]:
                points = float_round(line['points'], precision_rounding=0.01)
                partner_id = self._process_partner_id(line['partner'].strip())
                self._process_loyalty(partner_id, loyalty_group, points)
        return 'successfully updated loyalties'

    @http.route('/savings/upload', type="json", csrf="None", auth="public", methods=['GET', 'POST'])
    def savings(self, **kw):
        data = json.loads(request.httprequest.get_data()).get('payload')
        group_model = request.env['savings.group'].sudo()
        for group in data:
            savings_group = group_model.search([('name', '=', group.strip())], limit=1)
            if not group:
                return f'Missing group {group}'
            for line in data[group]:
                points = float_round(line['points'], precision_rounding=0.01)
                partner_id = self._process_partner_id(line['partner'].strip())
                self._process_savings(partner_id, savings_group, points)
        return 'successfully updated savings'
