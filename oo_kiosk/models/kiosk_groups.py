# -*- coding: utf-8 -*-

from odoo import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_kiosk_bom = fields.Boolean(string='Kiosk Bom')


class KioskGroups(models.Model):
    _name = 'kiosk.group'
    _description = 'Kiosk Product Group'
    _order = 'sequence asc'

    name = fields.Char()
    sequence = fields.Integer(string='Sequence')
    product_id = fields.Many2one('product.product', string='Consumed Product')
    quantity = fields.Float(string='Quantity')
    package_lines = fields.One2many('kiosk.package.line', inverse_name='group_id', string='Package Lines')


class KioskPackageLine(models.Model):
    _name = 'kiosk.package.line'
    _description = 'Packaging group lines'

    bom_id = fields.Many2one('mrp.bom', string='Bom', required=True, domain=[('is_kiosk_bom', '=', True)])
    related_group_ids = fields.Many2many('kiosk.group', string='Related Groups')
    group_id = fields.Many2one('kiosk.group', string='Group')
