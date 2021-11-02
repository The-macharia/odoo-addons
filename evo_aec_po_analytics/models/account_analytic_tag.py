# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'
    
    category = fields.Selection(selection=[('dept', '[DEPT] Department'), ('actv', '[ACTV] Activity'), ('loct', '[LOCT] Location'), ('part', '[PART] Partner')], string="Category")
