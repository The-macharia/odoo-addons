# -*- coding: utf-8 -*-


from odoo import models


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'sms.oo.sms']

    def action_post(self):
        res = super().action_post()
        params = self.env['ir.config_parameter'].sudo()
        sms_allowed = params.get_param('oo_sms_sms.invoice_enabled')
        if sms_allowed:
            for rec in self:
                numbers = rec._format_and_validate_number(rec.partner_id)
                rec._raise_validation_error(numbers)
                rec._send_sms(numbers)
        return res


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'sms.oo.sms']

    def action_post(self):
        res = super().action_post()
        params = self.env['ir.config_parameter'].sudo()
        sms_allowed = params.get_param('oo_sms_sms.payment_enabled')
        if sms_allowed:
            for rec in self.filtered(lambda p: not p.is_internal_transfer):
                numbers = rec._format_and_validate_number(rec.partner_id)
                rec._raise_validation_error(numbers)
                rec._send_sms(numbers)
        return res


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'sms.oo.sms']

    def action_confirm(self):
        res = super().action_confirm()
        params = self.env['ir.config_parameter'].sudo()
        sms_allowed = params.get_param('oo_sms_sms.sales_enaled')
        if sms_allowed:
            for rec in self:
                numbers = rec._format_and_validate_number(rec.partner_id)
                rec._raise_validation_error(numbers)
                rec._send_sms(numbers)
        return res


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'sms.oo.sms']

    def button_confirm(self):
        res = super().button_confirm()
        params = self.env['ir.config_parameter'].sudo()
        sms_allowed = params.get_param('oo_sms_sms.purchase_enabled')
        if sms_allowed:
            for rec in self:
                numbers = rec._format_and_validate_number(rec.partner_id)
                rec._raise_validation_error(numbers)
                rec._send_sms(numbers)
        return res
