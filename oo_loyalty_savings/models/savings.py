# -*- coding: utf-8 -*-


from odoo import api, fields, models


class SavingsGroup(models.Model):
    _name = 'savings.group'
    _description = 'Savings groups management'

    name = fields.Char(string='Name', required=True)
    members_count = fields.Integer(string='Total Members', compute="_compute_members_count")
    amount_tosave = fields.Float(string='Amount To Save')
    min_amount = fields.Float(string='Minimum Redeemable Points')
    product_ids = fields.Many2many('product.product', string='Products', domain=[('is_sub_product', '=', True)])
    active = fields.Boolean(string='Active', default=True)

    def _compute_members_count(self):
        for rec in self:
            rec.members_count = self.env['saving.saving'].search_count([('group_id', '=', rec.id)])

    def action_list_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Group Members',
            'res_model': 'saving.saving',
            'view_mode': 'tree,form',
            'domain': [('group_id', '=', self.id)],
        }


class Savings(models.Model):
    _name = 'saving.saving'
    _description = 'Partner savings management'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    group_id = fields.Many2one('savings.group', string='Saving Group', required=True)
    date_enrolled = fields.Date(string='Date Enrolled', required=True)
    date_exited = fields.Date(string='Date Exited')
    total_savings = fields.Float(string='Total Savings', readonly=True, compute="_compute_total_savings", store=True)
    saving_lines = fields.One2many('collection.line', 'saving_id', string='Saving Lines',
                                   domain=[('collection_type', '=', 'savings')])
    redeem_lines = fields.One2many('redeem.line', inverse_name='saving_id',
                                   string='Redeem Lines', domain=[('redeem_type', '=', 'savings')])

    @api.depends('saving_lines', 'saving_lines.points')
    def _compute_total_savings(self):
        for rec in self:
            amount = rec.mapped('saving_lines').filtered(
                lambda s: s.collection_type == 'savings').mapped('amount') or [0]
            rec.total_savings = sum(amount)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res:
            res.partner_id.savings_id = res.id
        return res

    def write(self, vals):
        res = super().write(vals)
        if res and vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            partner.savings_id = self.id
