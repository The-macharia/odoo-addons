# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_default_staff_comm = fields.Boolean(
        'Is default Staff Commission', compute='_compute_is_default_staff_comm')
    has_kcm = fields.Boolean(string='Has KCM?', store=True)
    kcm_partner_id = fields.Many2one(
        'res.partner', string='Kcm Customer', store=True)
    kcm_percentage = fields.Selection(
        string='Commision Percentage (%)', selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], store=True)
    sale_comm_percentage = fields.Selection(
        string='Newmatic Percentage', selection=[('1', '1'), ('2', '2'), ('3', '3')], store=True, help="Defaults to 1.5% if none of the lines quantity is greater than or equal to 10")

    is_a_kcm_bill = fields.Boolean(string='Is a KCM Bill?', store=True)
    kcm_origin_id = fields.Many2one('account.move', string='KCM Origin')

    total_kcm_commission_bills = fields.Integer(
        string='Total KCM Bills', compute="_compute_created_bils")
    total_sales_commission = fields.Monetary(
        string='Total Sales Commission', readonly=True)

    @api.depends('invoice_line_ids', 'invoice_line_ids.quantity')
    def _compute_is_default_staff_comm(self):
        for rec in self:
            if rec.invoice_line_ids.filtered(lambda line: line.quantity >= 10):
                self.is_default_staff_comm = False
            else:
                self.is_default_staff_comm = True

    def _compute_created_bils(self):
        for rec in self:
            kcm_invoices = self.env['account.move'].search_count(
                [('move_type', 'in', ['in_invoice']), ('kcm_origin_id', '=', rec.id)])

            rec.total_kcm_commission_bills = kcm_invoices

    def _prepare_kcm_commission_bill_vals(self):
        taxes = self.env['res.config.settings'].search([]).mapped('kcm_tax_id')

        journal_id = self.env['account.move'].with_context(
            default_move_type='in_invoice')._get_default_journal()

        if not journal_id:
            raise ValidationError(
                'You need to configure a default vendor bill journal for this transaction')

        if not self.kcm_percentage:
            raise ValidationError(
                'You need to set the KCM percentage!')

        return {
            'move_type': 'in_invoice',
            'is_a_kcm_bill': True,
            'invoice_date': self.invoice_date,
            'partner_id': self.kcm_partner_id.id,
            'kcm_origin_id': self.id,
            'journal_id': journal_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Kcm bill for {self.kcm_partner_id.name}',
                'quantity': 1.0,
                'price_unit': self.amount_untaxed * int(self.kcm_percentage) / 100,
                'tax_ids': [(4, taxes.id)] if taxes else False
            })],
        }

    def create_kcm_commission_bill(self):
        """Create a bill if an invoice is a marked as to have kcm
        Invoice line price unit is calculated as the kcm_percentage * total untaxed amount
        Taxes are set in res config, accounting section"""

        for rec in self:
            vals = rec._prepare_kcm_commission_bill_vals()
            bill_id = self.env['account.move'].create(vals)
            rec.total_kcm_commission_bills = rec.total_kcm_commission_bills + 1

    def _get_newmatic_sales_commission(self):
        amount = 0.48 * self.amount_untaxed
        above_10 = self.invoice_line_ids.filtered(lambda x: x.quantity >= 10)

        if above_10:
            commission = amount * int(self.sale_comm_percentage) / 100
        else:
            commission = 0.7 * (amount * 0.015)

        return commission

    def _prepare_sale_commission_values(self, amount):
        return {
            'date': self.invoice_date,
            'amount': amount,
            'user_id': self.invoice_user_id.id,
            'employee_id': self.invoice_user_id.employee_id.id,
            'invoice_id': self.id,
            'confirm_uid': self.env.user.id,
        }

    def update_salesperson_commission(self):
        """Adds the commission amount on the salesperson contract commission field

        line_amount =Amount to be considered is 48% of the invoice line subtotal
        For every invoice line with quantity above 10, percentage value (1 -3) * line_amount
        Below 10, commission is line_amount * 1.5%
        partner_id is assumed to be the sales agent"""

        for rec in self:
            if rec.state not in 'posted':
                raise ValidationError(
                    'An Invoice has to have been posted before creating a commission! Cancelled and Draft entries are disregarded.')

            commission = rec._get_newmatic_sales_commission()
            self.env['sale.commission'].create(
                rec._prepare_sale_commission_values(commission))

            if rec.invoice_user_id:
                salesperson_id = rec.invoice_user_id.employee_id or self.env['hr.employee'].search(
                    [('user_id', '=', rec.invoice_user_id.id)])

            if not salesperson_id:
                raise ValidationError(
                    'An invoice has to have a sales agent before creating this commission. Check that added salesperson has an employee attached to them or the the sales agent employee record has a user attached to it.')

            current_commission = salesperson_id.contract_id.commission
            salesperson_id.contract_id.commission = current_commission + commission

            rec.total_sales_commission = rec.total_sales_commission + commission

    def _return_invoice_view(self, invoices):
        """returns an action that display existing vendor bills depending on passed bill ids
            When only one found, show the vendor bill immediately.
        """

        result = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + \
                    [(state, view)
                     for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    def show_kcm_commission_bills(self):
        invoices = self.env['account.move'].search(
            [('move_type', 'in', ['in_invoice']), ('kcm_origin_id', '=', self.id)])

        return self._return_invoice_view(invoices)
