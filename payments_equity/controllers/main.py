# -*- coding: utf-8 -*-
from unittest import result
from odoo import http
from odoo.http import request

import xmltodict

import logging
_logger = logging.getLogger(__name__)

RESULT_CODES = {
    'Success': 000,
    'Invalid_Till_Number': 501,
    'Invalid_Username': 501,
    'Invalid_Password': 501,
    'Invalid_Amount': 502,
    'Invalid_Transaction_Ref': 502,
    'Invalid_Phonenumber': 502,
    'Internal_System_Error': 555
}

class PaymentsEquity(http.Controller):
    
    @http.route('/register-equity-payments', auth='public', csrf=None)
    def register_equity_payments(self, **kw):
        _logger.info('this ctrl is hit')
        data = xmltodict.parse(request.httprequest.get_data())
        acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'equity')], limit=1)
        result_code, transaction_no = self.authorise_transaction(data, acquirer)
        _logger.info(f'**********************result code tx_no {result_code} {transaction_no}')
        return self.return_response(result_code, transaction_no)

    def authorise_transaction(self, data, acquirer):
        if acquirer:
            confirmed_credentials, credentials_comment = self.confirm_credentials(acquirer, data)
            valid_data, payment_data, data_comment = self.check_data_validity(acquirer, data)
            if confirmed_credentials and valid_data:
                self.create_transaction(acquirer, payment_data)
                return ('Success', payment_data.get('acquirer_reference', False))
            if not confirmed_credentials:
                return (credentials_comment, payment_data.get('acquirer_reference', False))
            if not valid_data:
                return (data_comment, payment_data.get('acquirer_reference', False))
        return ('Internal_System_Error', data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('transactionRefNo', False))

    def confirm_credentials(self, acquirer, data):
        credentials = {}
        credentials['password'] = data.get('soapenv:Envelope', {}).get('soapenv:Header', {}).get('password', '')
        credentials['username'] = data.get('soapenv:Envelope', {}).get('soapenv:Header', {}).get('username', '')
        credentials['till'] = data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('TillNumber', '')
        return acquirer.check_credentials(credentials)

    def check_data_validity(self, acquirer, data):
        return acquirer.check_data(data)

    def create_transaction(self, acquirer, payment_data):
        acquirer.create_tx(payment_data)

    def return_response(self, result_code, transaction_no):
        return """<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
<env:Header/>
<env:Body>
<ns3:createEazzyTransactionResponse xmlns="" xmlns:ns3="http://pgw.equitybankgroup.com">
<return>
<status>%s</status>
<statusDescpription>%s</statusDescpription>
<transactionid>%s</transactionid>
</return>
</ns3:createEazzyTransactionResponse>
</env:Body>
</env:Envelope>""" % (RESULT_CODES[result_code], result_code, transaction_no)