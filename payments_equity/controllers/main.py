# -*- coding: utf-8 -*-
from unittest import result
import json
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

RESPONSE = """<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
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
    </env:Envelope>"""

class PaymentsEquity(http.Controller):
    
    @http.route('/register-equity-payments', auth='public', csrf=None, website=True)
    def register_equity_payments(self, **kw):
        if request.httprequest.get_data():
            ip = request.httprequest.remote_addr
            return self.return_response(request_data=request.httprequest.get_data(), ip=ip)
        return self.return_response(null=['Internal_System_Error', 'null'])

    def authorise_transaction(self, request_data, ip):
        data_comment = ''
        acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'equity')], limit=1)
        if acquirer:
            data = xmltodict.parse(request_data)
            data['transaction_ip_source'] = ip
            payment_request = acquirer.create_payment_request(acquirer, request_data, json.dumps(data))
            confirmed_credentials, credentials_comment = acquirer.check_credentials(data)
            if confirmed_credentials:
                valid_data, data_comment = acquirer.check_data(data)
            error_comment = credentials_comment if not confirmed_credentials else data_comment
            return {
                True: ('Success', data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('transactionRefNo', ''), payment_request),
                False: (error_comment, data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('transactionRefNo', ''), payment_request)
            }[confirmed_credentials and valid_data]
        return ('Internal_System_Error', data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('transactionRefNo', False), None)

    def return_response(self, request_data=None, ip=None, null=False):
        if not null:
            result_code, transaction_no, payment_request = self.authorise_transaction(request_data, ip)
            response = RESPONSE % (RESULT_CODES[result_code], result_code, transaction_no)
            if payment_request:
                payment_request.acknowledge_response(response)
            return response
        else:
            return RESPONSE % (RESULT_CODES[null[0]], null[0], null[1])