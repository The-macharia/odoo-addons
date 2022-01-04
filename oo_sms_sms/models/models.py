# -*- coding: utf-8 -*-


from odoo import api, fields, models
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

    def prepare_sms_data(self, phone):
        template = self.get_sms_template(self._name)
        if template:
            message = template.body
            message = message.strip().format(name=self.partner_id.name,
                                             number=self.name,
                                             amount=self.amount_residual)

            return {'to': phone, 'message': message}

    def post(self):
        res = super().post()
        for rec in self:
            phone = rec.partner_id.phone or rec.partner_id.mobile
            if phone:
                valid_number = rec.format_and_validate_number(rec.partner_id)
                if valid_number:
                    message = rec.prepare_sms_data(valid_number)
                    if message:
                        rec.send_sms(message)
            else:
                raise ValidationError(
                    "Selected customer does not have a valid phone or mobile number. \
                    Hint: Add a country to the partner's record for better validation.")

        return res
