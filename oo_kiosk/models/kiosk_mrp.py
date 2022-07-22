# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Mrp(models.Model):
    _inherit = 'mrp.production'

    kiosk_mrp_id = fields.Many2one('kiosk.mrp', string='Kiosk Mrp')

    # def action_confirm(self):
    #     raise ValidationError(self.move_finished_ids)


class KioskManufacturing(models.Model):
    _name = 'kiosk.mrp'

    name = fields.Char(string='Name', default='New', readonly="1")
    group_id = fields.Many2one('kiosk.group', string='Product Group')
    date_planned = fields.Datetime('Date Planned', default=datetime.now())
    mrp_type = fields.Selection(string='Type', selection=[('kiosk', 'Kiosk'), ('program', 'Program')], required=True)
    state = fields.Selection(string='Status', selection=[(
        'draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')], default='draft')
    mrp_ids = fields.Many2many(comodel_name='mrp.production', string='Mrp Orders')
    mrp_count = fields.Integer(string='Manufacturing Orders Count', compute='_compute_mrp_count')

    @api.model
    def create(self, vals):
        if vals.get('name') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('kiosk.order.sequence') or _('New')
        res = super().create(vals)
        return res

    @api.depends('mrp_ids')
    def _compute_mrp_count(self):
        for rec in self:
            rec.mrp_count = len(rec.mrp_ids)

    def get_mrps(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.group_id.name} Mrp Orders',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': [('kiosk_mrp_id', '=', self.id)]
        }

    def _get_default_locations(self):
        company_id = self.env.context.get('default_coompay_id', self.env.company.id)
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'mrp_operation'), ('warehouse_id.company_id', '=', company_id)])
        src_location = picking_type.default_location_src_id
        dest_location = picking_type.default_location_dest_id
        return src_location, dest_location

    def action_confirm(self):
        # TODO: when creating a mo in the same group, they should share the same picking. Use procurement_group to achieve this.
        # group_vals = []
        src_location_id, dest_location_id = self._get_default_locations()
        kiosk_lines = self.env['kiosk.group'].search([]).filtered(lambda k: k.package_lines).mapped('package_lines')
        procurement_group_id = False
        mrp_ids = []
        for line in kiosk_lines:
            vals = {
                'date_planned_start': self.date_planned,
                'product_id': line.bom_id.product_id.id,
                'product_uom_id': line.bom_id.product_id.uom_id.id,
                'bom_id': line.bom_id.id,
                'product_qty': 1,
                'kiosk_mrp_id': self.id,
                'location_src_id': src_location_id.id,
                'location_dest_id': dest_location_id.id,
                'procurement_group_id': procurement_group_id
            }
            # group_vals.append(vals)
            mo = self.env['mrp.production'].with_context({'import_file': True}).create(vals)
            mo._create_workorder()
            # procurement_group_id = mo.procurement_group_id.id
            mrp_ids.append(mo.id)
        self.write({
            'mrp_ids': [(6, 0, mrp_ids)],
            'state': 'posted'
        })

        # for mo in mos:
        #     # mo._onchange_product_id()
        #     # mo._onchange_bom_id()
        #     # mo._onchange_move_raw()
        #     mo._create_workorder()
        #     # mo._create_update_move_finished()

    def action_cancel(self):
        self.write({'state': 'cancel'})
        self.mrp_ids.action_cancel()
