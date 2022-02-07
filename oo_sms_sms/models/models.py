# -*- coding: utf-8 -*-


from odoo import fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_username = fields.Char(
        string='Username',
        default='sandbox',
        config_parameter='oo_sms_sms.sms_username')
    sms_api_key = fields.Char(
        string='Api Key',
        config_parameter='oo_sms_sms.sms_api_key')
    sms_shortcode = fields.Char(
        string="Shortcode", size=5,
        config_parameter='oo_sms_sms.sms_shortcode')
    sms_api_env = fields.Selection(selection=[
        ('live', 'Live'), ('sandbox', 'Sandbox'),
    ], string="SMS Mode", default='sandbox', config_parameter='oo_sms_sms.sms_api_env')


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'sms.oo.sms']

    def post(self):
        res = super().post()
        for rec in self:
            numbers = rec._format_and_validate_number(rec.partner_id)
            if not numbers:
                raise ValidationError(
                    "Customer does not have a valid phone number. \
                    Add a country to the customer's record for optimized validation.")
            rec._send_sms(numbers)
        return res
