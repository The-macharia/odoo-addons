from odoo import models, api, fields


class SalesCommission(models.Model):
    _name = 'sale.commission'
    _description = 'Reporting feature for sales commission'
    _order = 'date asc'

    date = fields.Date(string='Invoice Date', required=True, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, readonly=True)
    user_id = fields.Many2one('res.users', string='SalesPerson')
    invoice_id = fields.Many2one('account.move', string='Origin Invoice')
    amount = fields.Float(string='Amount', readonly=True)
    confirm_uid = fields.Many2one('res.users', string='Approved By')
    sale_id = fields.Many2one(
        'sale.order', string='Origin Sale Order', readonly=True)
    active = fields.Boolean(string='Active')

    def name_get(self):
        return [(rec.id, f'{rec.employee_id.name} {rec.invoice_id.name}') for rec in self]
