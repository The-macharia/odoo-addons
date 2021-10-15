# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     @api.multi
#     def _prepare_purchase_data(self):
#         data = []
#         for rec in self:
#             for line in rec.order_line:
#                 if line.make_to_order == 'sale' and line.product_id.seller_ids:
#                     vals = {
#                         'partner_id': line.product_id.seller_ids[0].mapped('name.id')[0],
#                         'date_order': rec.date_order,
#                         'currency_id': rec.currency_id.id,
#                         'company_id': rec.company_id.id,
#                         'sale_order_id': rec.id,
#                         'origin': rec.name,
#                         'order_line': [(0, 0, {
#                             'product_id': line.product_id.id,
#                             'name': line.product_id.display_name,
#                             'price_unit': 0,
#                             'account_analytic_id': rec.analytic_account_id.id,
#                             'date_planned': rec.date_order,
#                             'product_qty': line.product_uom_qty,
#                             'product_uom': line.product_uom.id,
#                         })]
#                     }
#                     data.append(vals)

#         return data

#     @api.multi
#     def action_confirm(self):
#         res = super().action_confirm()
#         data = self._prepare_purchase_data()

#         for rec in data:
#             self.env['purchase.order'].sudo().create(rec)

#         return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_analytic_id = fields.Many2one(
        'account.analytic.account', compute='compute_analytic_account', readonly=False)

    @api.depends('order_id', 'order_id.origin')
    def compute_analytic_account(self):
        for rec in self:
            if rec.order_id.origin:
                sale = self.env['sale.order'].search(
                    [('name', '=', rec.order_id.origin)]).mapped('analytic_account_id.id')
                if sale:
                    rec.account_analytic_id = int(sale[0])


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')
