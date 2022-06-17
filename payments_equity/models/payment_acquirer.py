# -*- coding: utf-8 -*-

import copy
import re
from datetime import datetime
import psycopg2
import requests

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
                return '+' + phone
        return False

    @api.model
    def create_payment_request(self, acquirer, request, json_request):
        # TODO: Check is self is valid
        return self.env['payment.transaction.request'].create({
            'acquirer_id': acquirer.id,
            'received_request': request,
            'json_request': json_request
        })

    @api.model
    def check_credentials(self, data):
        if self.equity_username != data.get('soapenv:Envelope', {}).get('soapenv:Header', {}).get('username', ''):
            return (False, 'Invalid_Username') 
        if self.equity_password != data.get('soapenv:Envelope', {}).get('soapenv:Header', {}).get('password', ''):
            return (False, 'Invalid_Password')
        if self.equity_till != data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('TillNumber', ''):
            return (False, 'Invalid_Till_Number')
        return (True, 'Success')

    @api.model
    def check_data(self, data):
        mobile = self.check_phone(data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('mobileNumber', False))
        amount = float(data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('amount', 0))
        mpesa_ref = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('additionalInfo', '')
        if mobile and amount > 0 and len(mpesa_ref) > 0:
            return (True, 'Success')
        if not mobile:
            return (False, 'Invalid_Phonenumber')
        if amount <= 0:
            return (False, 'Invalid_Amount')
        if not len(mpesa_ref):
            return (False, 'Invalid_MPesa_Ref')

    def get_payment_data(self, data):
        payment_data = {}
        payment_data['mobile'] = self.check_phone(data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('mobileNumber', False))
        payment_data['amount'] = float(data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('amount', 0))
        payment_data['transaction_timestamp'] = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('timeStamp', 0)
        payment_data['acquirer_reference'] = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('transactionRefNo', '')
        payment_data['mpesa_ref'] = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('additionalInfo', '')
        payment_data['paid_by'] = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('customerName', '')
        payment_data['transaction_ip_source'] = data.get('transaction_ip_source', '')
        return payment_data

    @api.model
    def create_tx(self, data):
        payment_data = self.get_payment_data(data)
        reference = self.env['payment.transaction']._compute_reference(
            self.provider)
        currency_id = self.env['res.currency'].search([('name', '=', 'KES')]).id
        partner_id, invoices = self.get_partner_id(payment_data['mobile'], payment_data['amount'])
        # partner_id = self.get_partner_id(payment_data['mobile'], payment_data['amount'])
        tx_values = {
            'acquirer_id': self.id,
            'reference': reference,
            'amount': payment_data['amount'],
            'acquirer_reference': payment_data['acquirer_reference'],
            'currency_id': currency_id,
            'partner_id': partner_id,
            'mobile': payment_data['mobile'],
            'transaction_timestamp': datetime.strptime(payment_data['transaction_timestamp'], '%Y%m%d%H%M%S'),
            'operation': 'online_direct',
            'invoice_ids': invoices if len(invoices) > 0 else False,
            'transaction_ip_source': payment_data.get('transaction_ip_source', ''),
            'mpesa_ref': payment_data['mpesa_ref'],
            'paid_by': payment_data['paid_by']
        }
        tx_sudo = self.env['payment.transaction'].sudo().create(tx_values)
        try:
            tx_sudo._finalize_post_processing()
            self.env.cr.commit()
        except psycopg2.OperationalError:  # A collision of accounting sequences occurred
            self.env.cr.rollback()  # Rollback and try later
        except Exception as e:
            _logger.exception(
                "encountered an error while post-processing transaction with id %s:\n%s",
                tx_sudo.id, e
            )
            self.env.cr.rollback()
        return tx_sudo

    @api.model
    def get_partner_id(self, mobile, amount):
        partner = self.env['res.partner'].sudo().search(['|', ('mobile', '=', mobile),('phone', '=', mobile)])
        if len(partner) > 1 or len(partner) == 0:
            return (self.equity_default_partner_id.id, [])
        if len(partner) == 1:
            partner = partner.parent_id.id or partner.id
            invoices = self.get_invoices(partner, amount)
            return (partner, invoices)
            # return partner

    @api.model
    def get_invoices(self, partner_id, amount):
        if partner_id != self.equity_default_partner_id.id:
            domain = [
                ('state', 'in', ('draft', 'posted')),
                ('payment_state', 'in', ('not_paid', 'partial')),
                ('move_type', '=', 'out_invoice'),
                ('payment_id', '=', False),
                ('partner_id', '=', partner_id)
            ]
            all_invoices = self.env['account.move'].sudo().search(domain, order='date asc')
            _logger.info('All invoices found in the system for partner {} :: {}.'.format(partner_id, all_invoices))
            if all_invoices:
                invoice_ids = []
                invoice_total = 0
                i = 0
                while invoice_total <= amount:
                    invoice_ids.append(all_invoices[i]['id'])
                    invoice_total += all_invoices[i]['amount_total_signed']
                    i +=1
                return [(6, 0, invoice_ids)]
            return []