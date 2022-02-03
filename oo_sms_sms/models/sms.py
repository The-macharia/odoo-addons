# -*- coding: utf-8 -*-

import json
import logging
import requests
from urllib.parse import urlencode

from odoo import models, _
from odoo.exceptions import UserError
from odoo.addons.phone_validation.models.phone_validation_mixin import PhoneValidationMixin as PVM
from odoo.addons.phone_validation.tools import phone_validation
import africastalking

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

    def get_sms_template(self, mode):
        template = self.env['sms.template'].search(
            [('model_id.model', '=', self._name)], limit=1)
        return template

    def _prepare_sms_data(self, numbers):
        template = self.get_sms_template(self._name)
        if template:
            message = template.body
            message = message.strip().format(name=self.partner_id.name,
                                             number=self.name,
                                             amount=self.amount_residual)

            return [message, numbers]

    def _send_sms(self, payload):
        username, api_key, sender = self._get_api_settings()
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS

        message, numbers = payload
        response = sms.send(message, numbers, sender_id=sender)
        _logger.error(response)
        return response

        # self.prepare_post_sms_notification(partners=[self.partner_id])
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

    def _format_and_validate_number(self, partner, company=None):
        if not partner.phone or partner.child_ids.mapped('phone'):
            return False

        if not company:
            company = partner.company_id or self._context.get('company_id')

        numbers = [self._validate_numbers(
            partner, company, partner.country_id)]

        for child in partner.child_ids.filtered('phone'):
            number = self._validate_numbers(child, company, partner.country_id)
            if number:
                numbers.append(number)

        return list(set(numbers))

    def _validate_numbers(self, partner, company, country, formats='E164'):
        phone_no = PVM.phone_format(
            partner, partner.phone, country=country, company=company)

        mobile_obj = phone_validation.phone_sanitize_numbers_w_record(
            [phone_no], country, force_format=formats)
        mobile = mobile_obj.get(phone_no)
        mobile = mobile.get('sanitized') or False
        return mobile
