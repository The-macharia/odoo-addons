# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    department_id = fields.Many2one('account.analytic.account', string='Department')
    activity_ids = fields.Many2many('account.analytic.tag', 'po_line_tag_activity_rel', 'activity_id', 'tag_id', string='Activity')
    location_ids = fields.Many2many('account.analytic.tag', 'po_line_tag_location_rel', 'location_id', 'tag_id', string='Location')
    partner_ids = fields.Many2many('account.analytic.tag', 'po_line_tag_partner_rel', 'partner_id', 'tag_id', string='Partner')
    
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        all_ids = []
        if line.department_id:
            line.account_analytic_id = line.department_id
        if line.activity_ids:
            all_ids += line.activity_ids.ids
        if line.location_ids:
            all_ids += line.location_ids.ids
        if line.partner_ids:
            all_ids += line.partner_ids.ids
        if len(all_ids) > 0:
            line.analytic_tag_ids = all_ids
        return line
    
    def write(self, values):
        if 'department_id' in values:
            values.update({'account_analytic_id': values.get('department_id')})
        all_ids = []
        if 'activity_ids' in values:
            all_ids += values.get('activity_ids')[0][2]
        else:
            all_ids += self.activity_ids.ids
        if 'location_ids' in values:
            all_ids += values.get('location_ids')[0][2]
        else:
            all_ids += self.location_ids.ids
        if 'partner_ids' in values:
            all_ids += values.get('partner_ids')[0][2]
        else:
            all_ids += self.partner_ids.ids
        values.update({'analytic_tag_ids': [(6, 0 , all_ids)]})
        result = super(PurchaseOrderLine, self).write(values)    
        return result
