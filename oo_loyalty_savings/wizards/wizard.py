# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class RedeemWizard(models.TransientModel):
    _name = 'redeem.wizard'
    _description = 'Redeem loyalty and saving points'

    collection_type = fields.Selection(selection=[('loyalty', 'Loyalty'), ('savings', 'Savings')],
                                       string='Collection Type', default='loyalty')
    points_to_redeem = fields.Float(string='Points to Redeem')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)

    def redeem_points(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')

        if self.collection_type == 'loyalty' and active_model != 'loyalty.loyalty':
            return
        elif self.collection_type == 'loyalty' and active_model == 'loyalty.loyalty':
            loyalty_id = self.env['loyalty.loyalty'].browse(active_id)
            if self.points_to_redeem > loyalty_id.total_points:
                raise ValidationError('You cannot redeem more points than the customer possess!')
            if loyalty_id.total_points < loyalty_id.group_id.min_points:
                raise ValidationError('This customer does not have the required threshold for withdrawing points!')
            points = self.points_to_redeem / loyalty_id.group_id.currency_points
            new_total_points = loyalty_id.total_points - points
            loyalty_id.write({
                'redeem_lines': [(0, 0, {
                    'redeem_type': 'loyalty',
                    'amount_redeemed': points,
                    'date': self.date,
                    'amount_before': loyalty_id.total_points,
                })],
                'total_points': new_total_points,
            })
            return True

        if self.collection_type == 'savings' and active_model != 'saving.saving':
            return
        elif self.collection_type == 'savings' and active_model == 'saving.saving':
            saving_id = self.env['saving.saving'].browse(active_id)
            if self.points_to_redeem > saving_id.total_savings:
                raise ValidationError('You cannot redeem more points than the customer possess!')
            if saving_id.total_savings < saving_id.group_id.min_amount:
                raise ValidationError('This customer does not have the required threshold for withdrawing points!')
            new_total_savings = saving_id.total_savings - self.points_to_redeem
            saving_id.write({
                'redeem_lines': [(0, 0, {
                    'redeem_type': 'savings',
                    'amount_before': saving_id.total_savings,
                    'amount_redeemed': self.points_to_redeem,
                    'date': self.date
                })],
                'total_savings': new_total_savings
            })
            return True
