# -*- coding: utf-8 -*-


import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class GroupCleanup(models.AbstractModel):
    _name = 'clean.group'

    def refresh_collection_lines(self):
        for rec in self:
            active_model = self._context.get('active_model')
            if active_model == 'loyalty.loyalty':
                lines = self.env['collection.line'].read_group(
                    [('loyalty_id', '=', rec.id)], ['date', 'invoice_line_id'], groupby='invoice_line_id', lazy=False)
                for line in lines:
                    if line['__count'] < 2 or not line.get('invoice_line_id'):
                        continue
                    collection_line = rec.loyalty_lines.filtered(
                        lambda l: l.invoice_line_id.id == line['invoice_line_id'][0]).sorted('id')
                    collection_line[:-1].unlink()
                    _logger.info(f'Loyalty lines deleted {collection_line.ids}')
            if active_model == 'saving.saving':
                lines = self.env['collection.line'].read_group(
                    [('saving_id', '=', rec.id)], ['date', 'invoice_line_id'], groupby='invoice_line_id', lazy=False)
                for line in lines:
                    if line['__count'] < 2 or not line.get('invoice_line_id'):
                        continue
                    collection_line = rec.saving_lines.filtered(
                        lambda l: l.invoice_line_id.id == line['invoice_line_id'][0]).sorted('id')
                    collection_line[:-1].unlink()
                    _logger.info(f'Saving lines deleted {collection_line.ids}')


class LoyaltyGroup(models.Model):
    _name = 'loyalty.group'
    _description = 'Loyalty groups management'

    name = fields.Char(string='Name', required=True, store=True)
    date_start = fields.Date(string='Start Date', required=True, store=True)
    date_end = fields.Date(string='End Date', store=True)
    members_count = fields.Integer(string='Total Members', compute="_compute_members_count")
    amount_for_point = fields.Integer(string='Amount for 1 Point', store=True)
    currency_points = fields.Integer(string='Conversion (Points for 1 KSH)', store=True)
    min_points = fields.Integer(string='Non Redeemable Amount', store=True)
    product_ids = fields.Many2many('product.product', string='Products', domain=[
                                   ('is_sub_product', '=', True)], store=True)
    active = fields.Boolean(string='Active', default=True)

    def _compute_members_count(self):
        for rec in self:
            rec.members_count = self.env['loyalty.loyalty'].search_count([('group_id', '=', rec.id)])

    def action_list_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'loyalty.loyalty',
            'name': f'{self.name} Group Members',
            'view_mode': 'tree,form',
            'domain': [('group_id', '=', self.id)],
        }


class Loyalty(models.Model):
    _name = 'loyalty.loyalty'
    _inherit = 'clean.group'
    _description = 'Partner loyalty management'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, store=True)
    group_id = fields.Many2one('loyalty.group', string='Loyalty Group', required=True, store=True)
    date_enrolled = fields.Date(string='Date Enrolled', required=True, store=True)
    date_exited = fields.Date(string='Date Exited')
    total_points = fields.Float(string='Total Points', compute="_compute_total_points", store=True)
    loyalty_lines = fields.One2many('collection.line', 'loyalty_id',
                                    string='Loyalty Lines', domain=[('collection_type', '=', 'loyalty')])
    redeem_lines = fields.One2many('redeem.line', inverse_name='loyalty_id',
                                   string='Redeem Lines', domain=[('redeem_type', '=', 'loyalty')])

    @api.depends('loyalty_lines', 'loyalty_lines.points')
    def _compute_total_points(self):
        for rec in self:
            total_amount = rec.mapped('loyalty_lines').filtered(
                lambda s: s.collection_type == 'loyalty').mapped('points') or [0]
            redeem_amount = rec.mapped('redeem_lines').filtered(
                lambda s: s.redeem_type == 'loyalty').mapped('amount_redeemed') or [0]
            rec.total_points = sum(total_amount) - sum(redeem_amount)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res:
            res.partner_id.loyalty_id = res.id
        return res

    def write(self, vals):
        res = super().write(vals)
        if res and vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            partner.loyalty_id = self.id


class CollectionLines(models.Model):
    _name = 'collection.line'
    _description = 'Loyalty and savings collection lines'
    _order = 'date desc'

    loyalty_id = fields.Many2one('loyalty.loyalty', string='Loyalty')
    saving_id = fields.Many2one('saving.saving', string='Savings')
    points = fields.Float(string='Points Gained')
    amount = fields.Float(string='Extra Coin')
    invoice_id = fields.Many2one(related='invoice_line_id.move_id', string='Invoice')
    invoice_line_id = fields.Many2one('account.move.line', string='Journal Item')
    amount_total = fields.Float(string='Total Amount')
    date = fields.Date(string='Date', required=True)
    collection_type = fields.Selection(selection=[('loyalty', 'Loyalty'), ('savings', 'Savings')],
                                       string='Collection Type', required=True, default='loyalty')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    points_worth = fields.Float(string='Points Worth', readonly=True)


class RedeemLines(models.Model):
    _name = 'redeem.line'
    _description = 'Loyalty and savings redemption lines'
    _order = 'date desc'

    loyalty_id = fields.Many2one('loyalty.loyalty', string='Loyalty')
    saving_id = fields.Many2one('saving.saving', string='Savings')
    amount_before = fields.Float(string='Points Before')
    amount_redeemed = fields.Float(string='Amount Redeemed')
    date = fields.Date(string='Date', required=True)
    amount_balance = fields.Float(string='Amount Balance', compute='_compute_points_balance')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    redeem_type = fields.Selection(selection=[('loyalty', 'Loyalty'), ('savings', 'Savings')],
                                   string='Redeem Type', default='loyalty')
    points_worth = fields.Float(string='Points Worth', readonly=True)

    @api.depends('amount_before', 'amount_redeemed')
    def _compute_points_balance(self):
        for rec in self:
            rec.amount_balance = rec.amount_before - rec.amount_redeemed
