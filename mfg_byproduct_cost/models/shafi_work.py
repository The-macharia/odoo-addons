from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_round


class mrpadd(models.Model):
    _inherit = 'mrp.bom.byproduct'

    cost_a = fields.Float(string='Cost')
    totals_a = fields.Float(string='Total amount', compute='custom123')

    @api.onchange('product_id')
    def custom1(self):
        for s in self:
            s.cost_a = s.product_id.standard_price

    @api.depends('product_qty')
    @api.onchange('product_id', 'product_qty')
    def custom123(self):
        for s in self:
            s.totals_a = s.cost_a * s.product_qty


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # def _cal_price(self, consumed_moves):
    #     """Set a price unit on the finished move according to `consumed_moves`.
    #     """
    #     super(MrpProduction, self)._cal_price(consumed_moves)
    #     work_center_cost = 0
    #     a = 0.0
    #     finished_move = self.move_finished_ids.filtered(
    #         lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
    #     if self.bom_id.byproduct_ids:
    #         for s in self.bom_id.byproduct_ids:
    #             a = a + (s.cost_a * s.product_qty) * self.product_qty
    #     if finished_move:
    #         finished_move.ensure_one()
    #         for work_order in self.workorder_ids:
    #             time_lines = work_order.time_ids.filtered(lambda x: x.date_end and not x.cost_already_recorded)
    #             duration = sum(time_lines.mapped('duration'))
    #             time_lines.write({'cost_already_recorded': True})
    #             work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
    #         if finished_move.product_id.cost_method in ('fifo', 'average'):
    #             qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done,
    #                                                                    finished_move.product_id.uom_id)
    #             finished_move.price_unit = (sum([-m.value for m in consumed_moves]) + work_center_cost - a) / qty_done
    #             finished_move.value = sum([-m.value for m in consumed_moves]) + work_center_cost
    #     return True

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        super(MrpProduction, self)._cal_price(consumed_moves)
        work_center_cost = 0
        finished_move = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            a = 0
            if self.bom_id.byproduct_ids:
                for s in self.bom_id.byproduct_ids:
                    a = a + (s.cost_a * s.product_qty) * self.product_qty
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(
                    lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                time_lines.write({'cost_already_recorded': True})
                work_center_cost += (duration / 60.0) * \
                                    work_order.workcenter_id.costs_hour
            qty_done = finished_move.product_uom._compute_quantity(
                finished_move.quantity_done, finished_move.product_id.uom_id)
            extra_cost = self.extra_cost * qty_done
            total_cost = (sum(
                -m.stock_valuation_layer_ids.value for m in consumed_moves.sudo()) + work_center_cost + extra_cost - a)
            byproduct_moves = self.move_byproduct_ids.filtered(
                lambda m: m.state not in ('done', 'cancel') and m.quantity_done > 0)
            byproduct_cost_share = 0
            for byproduct in byproduct_moves:
                if byproduct.cost_share == 0:
                    continue
                byproduct_cost_share += byproduct.cost_share
                if byproduct.product_id.cost_method in ('fifo', 'average'):
                    byproduct.price_unit = total_cost * byproduct.cost_share / 100 / byproduct.product_uom._compute_quantity(
                        byproduct.quantity_done, byproduct.product_id.uom_id)
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                finished_move.price_unit = total_cost * float_round(1 - byproduct_cost_share / 100,
                                                                    precision_rounding=0.0001) / qty_done
        return True


class MrpCostStructure12(models.AbstractModel):
    _inherit = 'report.mrp_account_enterprise.mrp_cost_structure'

    # @api.multi
    def get_lines(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0
            total_cost1 = 0.0

            # get the cost of operations
            operations = []
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                query_str = """SELECT w.operation_id, op.name, partner.name, sum(t.duration), wc.costs_hour
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder w ON (w.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id )
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (w.operation_id = op.id)
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY w.operation_id, op.name, partner.name, t.user_id, wc.costs_hour
                                ORDER BY op.name, partner.name
                            """
                self.env.cr.execute(query_str, (tuple(Workorders.ids),))
                for wo_id, op_id, wo_name, user, duration, cost_hour in self.env.cr.fetchall():
                    operations.append([user, op_id, wo_name, duration / 60.0, cost_hour])

            by_product_moves = []
            h = productions.product_qty
            if productions.bom_id.byproduct_ids:
                for q in productions.bom_id.byproduct_ids:
                    by_product_moves.append({
                        'product_ids': q.product_id,
                        'costs': q.cost_a,
                        'cost_a': q.cost_a * h * q.product_qty,
                        'qty1': h * q.product_qty,
                    })
            # get the cost of raw material effectively used
            raw_material_moves = []
            query_str = """SELECT
                                            sm.product_id,
                                            mo.id,
                                            abs(SUM(svl.quantity)),
                                            abs(SUM(svl.value))
                                         FROM stock_move AS sm
                                   INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                                   LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
                                        WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                                     GROUP BY sm.product_id, mo.id"""
            self.env.cr.execute(query_str, (tuple(mos.ids),))
            for product_id, mo_id, qty, cost in self.env.cr.fetchall():
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                })
                total_cost += cost

            # Get the cost of scrapped materials
            scraps = StockMove.search(
                [('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])
            uom = mos and mos[0].product_uom_id
            mo_qty = 0
            if any(m.product_uom_id.id != uom.id for m in mos):
                uom = product.uom_id
                for m in mos:
                    qty = sum(
                        m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped(
                            'product_uom_qty'))
                    if m.product_uom_id.id == uom.id:
                        mo_qty += qty
                    else:
                        mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            else:
                for m in mos:
                    mo_qty += sum(
                        m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped(
                            'product_uom_qty'))
            for m in mos:
                byproduct_moves = m.move_finished_ids.filtered(
                    lambda mo: mo.state != 'cancel' and mo.product_id != product)
            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'currency': self.env.company.currency_id,
                'raw_material_moves': raw_material_moves,
                'total_cost': total_cost,
                'scraps': scraps,
                'mocount': len(mos),
                'byproduct_moves': byproduct_moves,
                'by_product_moves': by_product_moves
            })
        return res
