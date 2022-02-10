# -*- coding: utf-8 -*-


from odoo import models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'sms.oo.sms']

    def action_post(self):
        res = super().action_post()
        for rec in self:
            numbers = rec._format_and_validate_number(rec.partner_id)
            rec._raise_validation_error(numbers)
            rec._send_sms(numbers)
        return res


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'sms.oo.sms']

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            numbers = rec._format_and_validate_number(rec.partner_id)
            if not numbers:
                raise ValidationError(
                    "Customer does not have a valid phone number. \
                    Add a country to the customer's record for optimized validation.")
            rec._send_sms(numbers)
        return res


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'sms.oo.sms']

    def button_confirm(self):
        res = super().button_confirm()
        for rec in self:
            numbers = rec._format_and_validate_number(rec.partner_id)
            if not numbers:
                raise ValidationError(
                    "Customer does not have a valid phone number. \
                    Add a country to the customer's record for optimized validation.")
            rec._send_sms(numbers)
        return res
