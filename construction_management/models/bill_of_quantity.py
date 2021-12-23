# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class bill_quantity(models.Model):
    _name = 'bill.quantity'
    _inherit = ['mail.thread']
    _rec_name = 'project_id'

    # @api.depends('quantity_line','quantity_line.price_subtotal')
    # def _compute_amount(self):
    #     material_price_subtotal = 0.0
    #     labor_price_subtotal = 0.0
    #     subcontract_price_subtotal = 0.0
    #     equipment_price_subtotal = 0.0
    #     work_package_price_subtotal = 0.0
    #     for i in self:
    #         if i.quantity_line:
    #             for record in i.quantity_line:
    #                 print("record.price_subtotal.................",record.price_subtotal)
    #                 if record.key == 'material':
    #                     material_price_subtotal = record.price_subtotal + material_price_subtotal
    #                     i.update({'material_cost': material_price_subtotal})
    #                 if record.key == 'labor':
    #                     labor_price_subtotal = record.price_subtotal + labor_price_subtotal
    #                     i.update({'labor_cost' : labor_price_subtotal})
    #                 if record.key == 'subcontract':
    #                     subcontract_price_subtotal = record.price_subtotal + subcontract_price_subtotal
    #                     i.update({'subcontract_cost' :subcontract_price_subtotal})
    #                 if record.key == 'work_package':
    #                     work_package_price_subtotal = record.price_subtotal + work_package_price_subtotal
    #                     i.update({'work_package_cost':work_package_price_subtotal})

    #        self.revision = 0

    project_id = fields.Many2one(
        'project.project', 'Project', track_visibility='always')
    revision = fields.Integer(
        'Revision', readonly=True)
    subcontract_cost = fields.Float(
        'Subcontract Cost',default = 0.0,  
        store=True,digits=dp.get_precision('Account'))
    material_cost = fields.Float(
        'Material Cost',
        readonly=True, default = 0.0,
        digits=dp.get_precision('Account'), )
    labor_cost = fields.Float(
        'Labor Cost',
        readonly=True, default = 0.0,
        digits=dp.get_precision('Account'), )
    work_package_cost = fields.Float(
        'Work Package Cost',
        readonly=True,default = 0.0,
        digits=dp.get_precision('Account'), )
    quantity_line = fields.One2many(
        'bill.quantity.line', 'bill_quantity_id',
        string='Bill Of Quantity Lines', readonly=False, copy=True)

    def create_new_revision(self):
        bill_line = []
        for line in self.quantity_line:
            bill_line.append(
                (0, False, {'product_id': line.product_id.id,
                            'type': line.type,
                            'uom_id': line.uom_id.id,
                            'description': line.description,
                            'qty': line.qty,
                            'bill_quantity_id': self.id,
                            'key': line.key,
                            'employee_id': line.employee_id.id,
                            'product_id': line.product_id.id,
                            'partner_id': line.partner_id.id,
                            'work_package_id': line.work_package_id.id,
                            'price_unit': line.price_unit,
                            'price_subtotal': line.price_subtotal,
                            }))
        vals = {'project_id': self.project_id.id,
                'quantity_line': bill_line
                }
        res = self.create(vals)
        res.revision = self.revision + 1


class bill_quantity_line(models.Model):
    _name = 'bill.quantity.line'
    _description = 'Bill Of Quantity Line'

    @api.depends('price_unit', 'qty', 'product_id')
    def _compute_price(self):
        for i in self:
            i.price_subtotal = i.qty * i.price_unit

    @api.model
    def create(self, vals):
        material_price_subtotal = 0.0
        labor_price_subtotal = 0.0
        subcontract_price_subtotal = 0.0
        equipment_price_subtotal = 0.0
        work_package_price_subtotal = 0.0
        res = super(bill_quantity_line, self).create(vals)
        if res.price_subtotal != 0.0:
            if res.bill_quantity_id:
                if res.key == 'material':
                    material_price_subtotal = res.price_subtotal + material_price_subtotal
                    res.bill_quantity_id.update({'material_cost': material_price_subtotal})
                if res.key == 'labor':
                    labor_price_subtotal = res.price_subtotal + labor_price_subtotal
                    res.bill_quantity_id.update({'labor_cost' : labor_price_subtotal})
                if res.key == 'subcontract':
                    subcontract_price_subtotal = res.price_subtotal + subcontract_price_subtotal
                    res.bill_quantity_id.update({'subcontract_cost' :subcontract_price_subtotal})
                if res.key == 'work_package':
                    work_package_price_subtotal = res.price_subtotal + work_package_price_subtotal
                    res.bill_quantity_id.update({'work_package_cost':work_package_price_subtotal})
        return res

    def write(self, vals):
        material_price_subtotal = 0.0
        labor_price_subtotal = 0.0
        subcontract_price_subtotal = 0.0
        equipment_price_subtotal = 0.0
        work_package_price_subtotal = 0.0        
        rslt = super(bill_quantity_line, self).write(vals)
        for i in self:
            if i.price_subtotal != 0.0:
                if i.bill_quantity_id:
                    if i.key == 'material':
                        material_price_subtotal = i.price_subtotal + material_price_subtotal
                        i.bill_quantity_id.update({'material_cost': material_price_subtotal})
                    if i.key == 'labor':
                        labor_price_subtotal = i.price_subtotal + labor_price_subtotal
                        i.bill_quantity_id.update({'labor_cost' : labor_price_subtotal})
                    if i.key == 'subcontract':
                        subcontract_price_subtotal = i.price_subtotal + subcontract_price_subtotal
                        i.bill_quantity_id.update({'subcontract_cost' :subcontract_price_subtotal})
                    if i.key == 'work_package':
                        work_package_price_subtotal = i.price_subtotal + work_package_price_subtotal
                        i.bill_quantity_id.update({'work_package_cost':work_package_price_subtotal})
        return rslt        

    #
    bill_quantity_id = fields.Many2one(
        'bill.quantity', string='Bill of Quantity Reference',
        ondelete='cascade', index=True)
    key = fields.Selection(
        [
            ('labor', 'Labor'),
            ('material', 'Material'),
            ('subcontract', 'Subcontract'),
            ('work_package', 'Work Package'),
        ], 'Key', default='labor')
    product_id = fields.Many2one(
        'product.product', string='Product',
        ondelete='restrict', index=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee', )
    # assest_id = fields.Many2one(
    #     'account.asset.asset',string='Assets',)
    partner_id = fields.Many2one(
        'res.partner', string='Partners', )
    work_package_id = fields.Many2one(
        'work.package', string='Work Package', )
    type = fields.Char('Type', size=64, )
    description = fields.Char(
        'Description', size=64, )
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', )
    qty = fields.Float("Qty", default=1)
    price_unit = fields.Float(
        "Rate", digits=dp.get_precision('Account'),default = 0.0, )
    price_subtotal = fields.Float(
        "Total", compute='_compute_price',default = 0.0,
        readonly=True, store=True,
        digits=dp.get_precision('Account'), )
# 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
