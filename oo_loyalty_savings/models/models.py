# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo.tools.float_utils import float_round


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

    def _calculate_loyalty_total_points(self, lines):
        total_points = 0
        for line in lines:
            total_points += line[-1]['points']
        return total_points

    def _calculate_savings_total_points(self, lines):
        total_amount = 0
        for line in lines:
            total_amount += line[-1]['amount']
        return total_amount

    def _process_loyalty_lines(self, payment_date, loyalty, lines):
        loyalty_lines = [(0, 0, {
            'date': payment_date,
            'invoice_line_id': line.id,
            'points': float_round(line.price_total / loyalty.group_id.amount_for_point, precision_rounding=0.01),
            'amount_total': line.price_total,
            'collection_type': 'loyalty',
            'points_worth': float_round(line.price_total / loyalty.group_id.amount_for_point, precision_rounding=0.01) / loyalty.group_id.currency_points
        }) for line in lines]

        total_points = self._calculate_loyalty_total_points(loyalty_lines) + loyalty.total_points
        return loyalty.write({'loyalty_lines': loyalty_lines, 'total_points': total_points})

    def _process_savings_lines(self, payment_date, saving, lines):
        saving_lines = [(0, 0, {
            'date': payment_date,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'invoice_line_id': line.id,
            'amount': saving.group_id.amount_tosave * line.quantity,
            'amount_total': line.price_total,
            'collection_type': 'savings',
        }) for line in lines]

        total_savings = saving.total_savings + self._calculate_savings_total_points(saving_lines)
        return saving.write({'saving_lines': saving_lines, 'total_savings': total_savings})

    def action_post(self):
        res = super().action_post()
        for rec in self:
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
