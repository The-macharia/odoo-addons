# -*- coding: utf-8 -*-


import logging

from odoo import api, fields, models
from odoo.tools.float_utils import float_round

MOVE_TYPE = {'out_invoice': 1, 'out_refund': -1}

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_sub_product = fields.Boolean(string='Subscription Product', store=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_id = fields.Many2one('loyalty.loyalty', string='Loyalty', store=True)
    loyalty_points = fields.Float(string='Loyalty Points', related='loyalty_id.total_points')
    savings_id = fields.Many2one('saving.saving', string='Savings', store=True)
    savings_points = fields.Float(related='savings_id.total_savings', string='Savings Points')
    total_crates = fields.Integer(string='Total Crates')

    def get_all_crates(self):
        pass

    def get_partner_loyalty(self):
        self.ensure_one()
        if self.loyalty_id:
            return {
                'type': 'ir.actions.act_window',
                'name': f'{self.name} Loyalty',
                'res_model': 'loyalty.loyalty',
                'view_mode': 'tree,form',
                'domain': [('partner_id', '=', self.id)]
            }
        else:
            pass

    def get_partner_savings(self):
        self.ensure_one()
        if self.savings_id:
            return {
                'type': 'ir.actions.act_window',
                'name': f'{self.name} Savings',
                'res_model': 'saving.saving',
                'view_mode': 'tree,form',
                'domain': [('partner_id', '=', self.id)]
            }
        else:
            pass


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _process_loyalty_lines(self, payment_date, loyalty, lines):
        loyalty_lines = []
        total_points = loyalty.total_points
        for line in lines:
            points = float_round(line.price_total / loyalty.group_id.amount_for_point, precision_rounding=0.01)
            points = points * MOVE_TYPE.get(self.move_type, 0)
            total_points += points
            loyalty_lines.append((0, 0, {
                'date': payment_date,
                'invoice_line_id': line.id,
                'points': points,
                'amount_total': line.price_total * MOVE_TYPE.get(self.move_type, 0),
                'collection_type': 'loyalty',
                'points_worth': points / loyalty.group_id.currency_points
            }))
        _logger.info(f'{self.move_type} LOYALTIES: {loyalty_lines}')
        return loyalty.write({'loyalty_lines': loyalty_lines, 'total_points': total_points})

    def _process_savings_lines(self, payment_date, saving, lines):
        total_savings = saving.total_savings
        saving_lines = []
        for line in lines:
            amount = saving.group_id.amount_tosave * line.quantity * MOVE_TYPE.get(self.move_type, 0)
            total_savings += amount
            saving_lines.append((0, 0, {
                'date': payment_date,
                'product_id': line.product_id.id,
                'quantity': line.quantity * MOVE_TYPE.get(self.move_type, 0),
                'invoice_line_id': line.id,
                'amount': amount,
                'amount_total': line.price_total * MOVE_TYPE.get(self.move_type, 0),
                'collection_type': 'savings',
            }))
        _logger.info(f'SAVINGS: {saving_lines}')
        return saving.write({'saving_lines': saving_lines, 'total_savings': total_savings})

    def action_post(self):
        res = super().action_post()
        for rec in self.filtered(lambda m: m.move_type in MOVE_TYPE.keys()):
            loyalty_id = rec.partner_id.loyalty_id
            loyalty_group = loyalty_id and loyalty_id.group_id or False
            if loyalty_group and loyalty_group.product_ids:
                lines = rec.invoice_line_ids.filtered(lambda l: l.product_id.id in loyalty_group.product_ids.ids)
                if lines:
                    rec._process_loyalty_lines(rec.invoice_date, loyalty_id, lines)

            savings_id = rec.partner_id.savings_id
            savings_group = savings_id and savings_id.group_id or False
            if savings_group and savings_group.product_ids:
                lines = rec.invoice_line_ids.filtered(lambda l: l.product_id.id in savings_group.product_ids.ids)
                if lines:
                    rec._process_savings_lines(rec.invoice_date, savings_id, lines)
        return res


class StockCrates(models.Model):
    _name = 'stock.crates'
    _inherit = ['mail.thread']
    _description = 'Issuing of crates to customers'
    _rec_name = 'partner_id'
    _order = 'id desc, date desc'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, tracking=True)
    date = fields.Date(string='Date', required=True, tracking=True)
    crates_issued = fields.Integer(string='Crates Issued', required=True, tracking=True)
    crates_returned = fields.Integer(string='Crates Returned', tracking=True)
    crates_remaining = fields.Integer(string='Crates Remaining', readonly=True,
                                      store=True, help="Crates remaining at this time.")
    state = fields.Selection(string='State', selection=[(
        'draft', 'Draft'), ('posted', 'Posted')], default='draft', tracking=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.crates_remaining = rec.partner_id.total_crates

    def action_approve(self):
        held_crates = self.crates_issued - self.crates_returned
        crates_remaining = self.partner_id.total_crates + held_crates
        crates_remaining = crates_remaining if crates_remaining > 0 else 0
        self.partner_id.total_crates = crates_remaining
        self.crates_remaining = crates_remaining
        self.write({'state': 'posted'})
