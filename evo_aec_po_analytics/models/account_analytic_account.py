# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    category = fields.Selection(selection=[('dept', '[DEPT] Department'), ('actv', '[ACTV] Activity'), ('loct', '[LOCT] Location'), ('part', '[PART] Partner')], string="Category")
