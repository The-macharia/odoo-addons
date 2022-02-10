# -*- coding: utf-8 -*-

import copy
import re
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

import logging
_logger = logging.getLogger(__name__)

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('equity', "Equity")], ondelete={'equity': 'set default'})
    equity_username = fields.Char(string='Username', required_if_provider='equity')
    equity_password = fields.Char('Password', required_if_provider='equity')
    equity_password_confirm = fields.Char('Confirm Password', required_if_provider='equity')
    equity_till = fields.Char('Till Number', required_if_provider='equity')
    equity_default_partner_id = fields.Many2one('res.partner', string='Default Partner', required_if_provider='equity')


    @api.model_create_multi
    def create(self, values_list):
        vl = copy.deepcopy(values_list)
        for values in vl:
            if values.get('provider', False) and values['provider'] == 'equity':
                equity_acquires = self.sudo().search([('provider', '=', 'equity')])
                if len(equity_acquires) > 0:
                    values_list.remove(values)
                if not self._equity_check_currency():
                    values_list.remove(values)
        return super().create(values_list)

    def _equity_check_currency(self):
        KES = self.env['res.currency'].search([('name', '=', 'KES')])
        if KES.active and KES.rate:
            return True
        return False

    @api.constrains('equity_password_confirm')
    def _check_password_match(self):
        for acquirer in self.filtered(lambda a: a.provider == 'equity'):
            if acquirer.equity_password_confirm != acquirer.equity_password:
                raise UserError(_('The passwords do not match. Please try again.'))

    @api.onchange('equity_password_confirm')
    def onchange_equity_password_confirm(self):
        if self.equity_password_confirm != self.equity_password:
            raise UserError(_('The passwords do not match. Please try again.'))

    @api.model
    def check_phone(self, phone):
        if phone:
            phone_regex = re.compile(r'(254)(\d{8})')
            match_object = phone_regex.search(phone)
            if match_object:
                return phone
        return False

    @api.model
    def check_credentials(self, credentials):
        if self.equity_username != credentials['username']:
            return (False, 'Invalid_Username')
        if self.equity_password != credentials['password']:
            return (False, 'Invalid_Password')
        if self.equity_till != credentials['till']:
            return (False, 'Invalid_Till_Number')
        return (True, 'Success')

    @api.model
    def check_data(self, data):
        mobile = self.check_phone(data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('mobileNumber', False))
        amount = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('amount', 0)
        acquirer_reference = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('transactionRefNo', '')
        payment_data = {}
        if mobile and int(amount) > 0 and len(acquirer_reference) > 0:
            payment_data['mobile'] = mobile
            payment_data['amount'] = int(amount)
            payment_data['transaction_timestamp'] = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('timeStamp', 0)
            payment_data['acquirer_reference'] = acquirer_reference
            return (True, payment_data, 'Success')
        if not mobile:
            return (False, payment_data, 'Invalid_Phonenumber')
        if int(amount) <= 0:
            return (False, payment_data, 'Invalid_Amount')
        if not len(acquirer_reference):
            return (False, payment_data, 'Invalid_Transaction_Ref')

    @api.model
    def create_tx(self, payment_data):
        reference = self.env['payment.transaction']._compute_reference(
            self.provider)
        currency_id = self.env['res.currency'].search([('name', '=', 'KES')]).id
        partner_id, invoices = self.get_partner_id(payment_data['mobile'], payment_data['amount'])
        # invoices = self.get_invoices(partner_id, payment_data['amount'])
        tx_values = {
            'acquirer_id': self.id,
            'reference': reference,
            'amount': payment_data['amount'],
            'acquirer_reference': payment_data['acquirer_reference'],
            'currency_id': currency_id,
            'partner_id': partner_id,
            'mobile': payment_data['mobile'],
            'transaction_timestamp': datetime.fromtimestamp(int(payment_data['transaction_timestamp'])),
            'operation': 'online_direct',
            'invoice_ids': invoices if len(invoices) > 0 else False
        }
        tx_sudo = self.env['payment.transaction'].sudo().create(tx_values)
        _logger.info(f'*****************tx_sudo {tx_sudo[0]}')
        tx_sudo._finalize_post_processing()
        return tx_sudo

    @api.model
    def get_partner_id(self, mobile, amount):
        partner = self.env['res.partner'].sudo().search(['|', ('mobile', '=', mobile),('phone', '=', mobile)])
        if len(partner) > 1 or len(partner) == 0:
            return self.equity_default_partner_id.id, []
        if len(partner) == 1:
            partner = partner.parent_id.id or partner.id
            invoices = self.get_invoices(partner, amount)
            return (partner, invoices)

    @api.model
    def get_invoices(self, partner_id, amount):
        domain = [
            ('state', 'in', ('draft', 'posted')),
            ('payment_state', '=', 'not_paid'),
            ('move_type', '=', 'out_invoice'),
            ('payment_id', '=', False)
        ]
        if partner_id != self.equity_default_partner_id.id:
            domain.append(('partner_id', '=', partner_id))
        all_invoices = self.env['account.move'].sudo().search(domain, order='date asc')
        invoices = self.env['account.move']
        invoice_total = 0
        i = 0
        while invoice_total <= amount:
            invoices |= all_invoices[i]
            invoice_total = all_invoices[i].amount_total_signed
        return [(6, 0, invoices.ids)]