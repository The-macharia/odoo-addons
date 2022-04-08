# -*- coding: utf-8 -*-

import logging

import africastalking
from odoo import _, models
from odoo.addons.phone_validation.tools.phone_validation import phone_sanitize_numbers
from odoo.exceptions import ValidationError
from functools import reduce
import operator
_logger = logging.getLogger(__name__)


class SmsOOSms(models.AbstractModel):
    _name = 'sms.oo.sms'
    _description = 'Abstract class for managing sms'

    def _get_api_settings(self):
        params = self.env['ir.config_parameter'].sudo()

        username = params.get_param('oo_sms_sms.sms_username').strip()
        key = params.get_param('oo_sms_sms.sms_api_key').strip()
        sender = params.get_param('oo_sms_sms.sms_shortcode').strip()
        return username, key, sender

    def get_sms_template(self):
        template = self.env['sms.template'].search(
            [('model_id.model', '=', self._name)], limit=1)
        return template

    def _prepare_sms_message(self):
        template = self.get_sms_template()
        MailRenderMixin = self.env['mail.render.mixin']

        if template and template.body:
            body = MailRenderMixin._render_template(
                template.body, self._name, [self.id], post_process=True)

            return body
        return {}

    def _send_sms_callback(self, error, response):
        _logger.error(error)
        _logger.info(response)
        {'SMSMessageData': {'Message': 'Sent to 3/3 Total Cost: KES 2.4000', 'Recipients': [{'statusCode': 101, 'number': '+254713235761', 'cost': 'KES 0.8000', 'status': 'Success', 'messageId': 'ATXid_17b373b919d633b5f187700791f49d0a'}, {
            'statusCode': 101, 'number': '+254720890160', 'cost': 'KES 0.8000', 'status': 'Success', 'messageId': 'ATXid_979457e5f6111c059dd67dbbb54bd019'}, {'statusCode': 101, 'number': '+254714452862', 'cost': 'KES 0.8000', 'status': 'Success', 'messageId': 'ATXid_244a21e775a9a6e3ad65bda8653e959b'}]}}

    def _send_sms(self, numbers):
        username, api_key, sender = self._get_api_settings()
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS

        message = self._prepare_sms_message().get(self.id, '')
        response = sms.send(message, numbers, sender_id=sender,
                            callback=self._send_sms_callback)
        _logger.error(response)
        self.message_post(body=f'Sent sms successfully to {numbers}')
        return response

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

    def _format_and_validate_number(self, partner):
        related_phone = partner.child_ids.mapped(lambda x: [x.mobile, x.phone])
        related_phone += [[partner.phone, partner.mobile]]
        numbers = set(filter(lambda x: x, reduce(operator.iconcat, related_phone, [])))
        if not numbers:
            return False
        country = partner.country_id
        numbers = [partner._phone_format(phone) for phone in numbers]
        numbers = list(set(filter(lambda n: n, numbers)))
        if numbers:
            sanitized = phone_sanitize_numbers(numbers, country.code, country.phone_code)
            return [num['sanitized'] for num in sanitized.values()]
        return False

    def _raise_validation_error(self, numbers):
        if not numbers:
            raise ValidationError(
                "Customer does not have a valid phone number. \
                    Add a country to the customer's record for optimized validation.")
