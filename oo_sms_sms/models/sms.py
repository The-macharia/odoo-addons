# -*- coding: utf-8 -*-

import json
import logging
import requests
from urllib.parse import urlencode

from odoo import models,_
from odoo.exceptions import UserError
from odoo.addons.phone_validation.models.phone_validation_mixin import PhoneValidationMixin as PVM
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)

urls = {
    'live': "https://api.africastalking.com/version1/messaging",
    'sandbox': "https://api.sandbox.africastalking.com/version1/messaging"
}


def _prepare_request_header(key):
    return {
        'Accept': 'application/json',
        'apiKey': key,
        'Content-Type': 'application/json',
    }


class SmsOOSms(models.AbstractModel):
    _name = 'sms.oo.sms'
    _description = 'Abstract class for managing sms'

    def _get_api_settings(self):
        params = self.env['ir.config_parameter'].sudo()
        return {
            'username': params.get_param('oo_sms_sms.sms_username').strip(),
            'key': params.get_param('oo_sms_sms.sms_api_key').strip(),
            'sender': params.get_param('oo_sms_sms.sms_shortcode').strip(),
            'env': params.get_param('oo_sms_sms.sms_api_env').strip(),
        }

    def send_sms(self, message):
        self.ensure_one()
        res = self._send_request(message)
        self.prepare_post_sms_notification(partners=[self.partner_id])
        # if res.get('Recipients'):
        #     recipient = res.get('Recipients')[0]
        #     self.write({
        #         'status': recipient['status'],
        #         'status_code': recipient['statusCode'],
        #         'message_id': recipient['messageId'],
        #         'json_response': recipient,
        #         # 'state': STAT_CODE_MAP.get(recipient['statusCode'])
        #     })
        return True

    def _send_request(self, payload):
        if payload is None:
            payload = {}
        config = self._get_api_settings()
        payload.update({
            'username': config.get('username'),
            'from': config.get('sender'),
        })

        if not all([config['username'], config['key'], config['sender'], config['env']]):
            raise UserError(
                _("Missing configuration for Africa's Talking Apis. Confirm that a Username,\
                 Api Key, Sender and Api environment are provided."))
        try:
            url = urls.get(config['env']),
            headers = _prepare_request_header(config.get('key'))
            response = requests.post(
                url,
                data=urlencode(payload),
                headers=headers
            )

            _logger.info(
                f'Status Code: {response.status_code} - AfricasTalking returned...{response.text}')
            response.raise_for_status()
            response = response.json()

        except Exception as e:
            message = f'Failed sending message with error {e}'
            _logger.error(message)

        # if not isinstance(response, dict):
        #     response = json.loads(response)
        # response = response.get('SMSMessageData')
        # return response

    # def _send_bulk_sms(self, message):
    #     recipients = [sms.number for sms in self]
    #     payload = {
    #         'to': ','.join(recipients),
    #         'message': message,
    #     }
    #     res = self._send_request(payload)
    #     for recipient in res.get('Recipients'):
    #         sms = self.filtered(lambda s: s.number == recipient['number'])
    #         sms.write({
    #             'status': recipient['status'],
    #             'status_code': recipient['statusCode'],
    #             'message_id': recipient['messageId'],
    #             'json_response': recipient,
    #             # 'state': STAT_CODE_MAP.get(recipient['statusCode'], 'pending')
    #         })
    #     return True

    def get_sms_template(self, mode):
        template = self.env['sms.template'].search(
            [('model_id.model', '=', self._name)], limit=1)
        return template

    def prepare_post_sms_notification(self, partners=None):
        subtype = self.env.ref('mail.mt_note')
        partners_to = False
        if partners:
            partners_to = [(4, partner.id) for partner in partners]
        return {
            'subject': 'Post SMS Notification',
            'model': self._name,
            'res_id': self.id,
            'message_type': 'notification',
            'subtype_id': subtype.id or False,
            'partner_ids': partners_to,
            'notified_partner_ids': partners_to,
        }

    def format_and_validate_number(self, partner, company=None):
        if not company:
            company = partner.company_id or self._context.get('company_id')
        phone_no = PVM.phone_format(self, partner.phone,
                                    country=partner.country_id, company=company)

        mobile_obj = phone_validation.phone_sanitize_numbers_w_record(
            [phone_no], self, partner.country_id, force_format='E164')
        mobile = mobile_obj.get(phone_no)
        mobile = mobile.get('sanitized') or False
        return mobile
