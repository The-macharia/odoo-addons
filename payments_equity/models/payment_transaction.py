# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    mobile = fields.Char('Mobile')
    transaction_timestamp = fields.Datetime('Transaction Timestamp')

    @api.model_create_multi
    def create(self, vals):
        txs = super().create(vals)
        for tx in txs:
            if tx.provider == 'equity':
                tx._set_done()
        return tx