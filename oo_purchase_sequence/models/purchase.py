# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_source = fields.Selection(string='Purchase source', selection=[
                                       ('import', 'Import'), ('local', 'Local')], required=True)

    @api.model
    def create(self, vals):
        if vals.get('purchase_source') and vals['purchase_source'] == 'import':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.import.sequence') or _('')
        res = super().create(vals)
        return res
