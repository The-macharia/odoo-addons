# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    department_id = fields.Many2one('account.analytic.account', string='Department')
    activity_ids = fields.Many2many('account.analytic.tag', 'ac_line_tag_activity_rel', 'activity_id', 'tag_id',
                                    string='Activity')
    location_ids = fields.Many2many('account.analytic.tag', 'ac_line_tag_location_rel', 'location_id', 'tag_id',
                                    string='Location')
    partner_ids = fields.Many2many('account.analytic.tag', 'ac_line_tag_partner_rel', 'partner_id', 'tag_id',
                                   string='Partner')

    @api.onchange('department_id', 'activity_ids', 'location_ids', 'partner_ids')
    def onchange_analytic_tags(self):
        self.ensure_one()
        if self.department_id:
            self.account_analytic_id = self.department_id.id
        elif not self.department_id:
            self.account_analytic_id = False

        # Update Analytic Tags         
        self.analytic_tag_ids = self.activity_ids + self.location_ids + self.partner_ids


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ~ we will map department_id, activity_ids, location_ids, partner_ids
    # ~ While create refund of vendor bill

    def _refund_cleanup_lines(self, lines):
        """ Convert records to dict of values suitable for one2many line creation

            :param recordset lines: records to convert
            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
        """
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.items():
                if name in MAGIC_COLUMNS:
                    continue
                elif field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
                elif name == 'invoice_line_tax_ids':
                    values[name] = [(6, 0, line[name].ids)]
                elif name in ['activity_ids', 'location_ids', 'partner_ids', 'analytic_tag_ids']:
                    values[name] = [(6, 0, line[name].ids)]
            result.append((0, 0, values))
        return result

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountMove, self)._prepare_invoice_line_from_po_line(line)
        data.update({
            'department_id': line.department_id.id,
            'activity_ids': line.activity_ids.ids,
            'location_ids': line.location_ids.ids,
            'partner_ids': line.partner_ids.ids,
            'account_analytic_id': line.department_id.id,
            'analytic_tag_ids': line.activity_ids.ids + line.location_ids.ids + line.partner_ids.ids,
        })
        return data

    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        """Return the additional move lines for purchase invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id
        if i_line.product_id and i_line.product_id.valuation == 'real_time' and i_line.product_id.type == 'product':
            # get the fiscal position
            fpos = i_line.invoice_id.fiscal_position_id
            # get the price difference account at the product
            acc = i_line.product_id.property_account_creditor_price_difference
            if not acc:
                # if not found on the product get the price difference account at the category
                acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ
            acc = fpos.map_account(acc).id
            # reference_account_id is the stock input account
            reference_account_id = i_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)[
                'stock_input'].id
            diff_res = []
            # calculate and write down the possible price difference between invoice price and product price
            for line in res:
                if line.get('invl_id', 0) == i_line.id and reference_account_id == line['account_id']:
                    valuation_price_unit = i_line.product_id.uom_id._compute_price(i_line.product_id.standard_price,
                                                                                   i_line.uom_id)
                    if i_line.product_id.cost_method != 'standard' and i_line.purchase_line_id:
                        # for average/fifo/lifo costing method, fetch real cost price from incomming moves
                        valuation_price_unit = i_line.purchase_line_id.product_uom._compute_price(
                            i_line.purchase_line_id.price_unit, i_line.uom_id)
                        stock_move_obj = self.env['stock.move']
                        valuation_stock_move = stock_move_obj.search(
                            [('purchase_line_id', '=', i_line.purchase_line_id.id), ('state', '=', 'done')])
                        if valuation_stock_move:
                            valuation_price_unit_total = 0
                            valuation_total_qty = 0
                            for val_stock_move in valuation_stock_move:
                                valuation_price_unit_total += val_stock_move.price_unit * val_stock_move.product_qty
                                valuation_total_qty += val_stock_move.product_qty
                            valuation_price_unit = valuation_price_unit_total / valuation_total_qty
                            valuation_price_unit = i_line.product_id.uom_id._compute_price(valuation_price_unit,
                                                                                           i_line.uom_id)
                    if inv.currency_id.id != company_currency.id:
                        valuation_price_unit = company_currency.with_context(date=inv.date_invoice).compute(
                            valuation_price_unit, inv.currency_id, round=False)
                    if valuation_price_unit != i_line.price_unit and line['price_unit'] == i_line.price_unit and acc:
                        # price with discount and without tax included
                        price_unit = i_line.price_unit * (1 - (i_line.discount or 0.0) / 100.0)
                        tax_ids = []
                        if line['tax_ids']:
                            # line['tax_ids'] is like [(4, tax_id, None), (4, tax_id2, None)...]
                            taxes = self.env['account.tax'].browse([x[1] for x in line['tax_ids']])
                            price_unit = taxes.compute_all(price_unit, currency=inv.currency_id, quantity=1.0)[
                                'total_excluded']
                            for tax in taxes:
                                tax_ids.append((4, tax.id, None))
                                for child in tax.children_tax_ids:
                                    if child.type_tax_use != 'none':
                                        tax_ids.append((4, child.id, None))
                        price_before = line.get('price', 0.0)
                        line.update({'price': company_currency.round(valuation_price_unit * line['quantity'])})
                        diff_res.append({
                            'type': 'src',
                            'name': i_line.name[:64],
                            'price_unit': company_currency.round(price_unit - valuation_price_unit),
                            'quantity': line['quantity'],
                            'price': company_currency.round(price_before - line.get('price', 0.0)),
                            'account_id': acc,
                            'product_id': line['product_id'],
                            'uom_id': line['uom_id'],
                            # ~ 'account_analytic_id': line['account_analytic_id'],
                            'department_id': line['department_id'],
                            'tax_ids': tax_ids,
                        })
            return diff_res
        return []
