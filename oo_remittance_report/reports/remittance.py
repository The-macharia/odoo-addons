from odoo import models, api, _
from odoo.tools import float_round
from odoo.exceptions import ValidationError


class RemittanceAdvice(models.AbstractModel):
    _name = 'report.oo_remittance_report.remittance_advice_report'
    _description = 'Remittance Advice Report'

    def _compute_wht_tax(self):
        d = []
        for line in self.invoice_line_ids:
            for tax in line.tax_ids:
                d.append(tax._compute_amount(
                    line.price_subtotal, line.price_unit))

        wht_tax = list(filter(lambda x: x < 0), d)

        return sum(wht_tax)

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        data = {}

        if any(docs.filtered(lambda doc: doc.state in ['draft', 'cancel'])):
            raise ValidationError(
                _('You have some bills in draft or cancelled state! Remittance report is only for Validated and Active Bills!'))

        for doc in docs:
            withholding = 0
            total = 0
            total_paid = 0
            total_net = 0
            amt = 0
            refund_amount = 0
            refund_wht = 0
            refund_net = 0
            refund_tax = 0

            type_ = -1 if doc.move_type == 'in_refund' else 1

            if doc.state != 'draft':
                desc = [line.name for line in max(
                    doc.invoice_line_ids, key=lambda x: x.price_subtotal)]
                val = {
                    'net': 0,
                    'vat': 0,
                    'non_vat': 0,
                    'amt': 0,
                    'inv': doc.name,
                    'date': doc.invoice_date.strftime('%d/%m/%Y'),
                    'description': desc[0] if desc else ''
                }

                paid = self.env['account.payment'].search(
                    [('ref', '=', doc.name)]).mapped('amount')

                val['paid'] = paid[0] if paid else 'Not Paid'

                for line in doc.invoice_line_ids:
                    if line.tax_ids:
                        total_net += line.price_subtotal * type_
                    else:
                        val['non_vat'] += line.price_subtotal * type_

                # if doc.tax_line_ids:
                #     for line in doc.tax_line_ids:
                #         if line.amount < 0:
                #             withholding += line.amount

                # for line in doc.refund_invoice_ids:
                #     refund_amount += line.amount_total
                #     refund_net += line.amount_untaxed
                #     refund_tax += line.amount_tax
                #     # refund_wht += sum(line.tax_line_ids.filtered(
                #     #     lambda r: r.amount < 0).mapped('amount'))
                #     refund_wht += line._compute_wht_tax()

                # withholding += refund_wht

                val['vat'] = float_round(
                    (doc.amount_tax - refund_tax - withholding), precision_digits=2, rounding_method='UP') * type_
                val['net'] = float_round(
                    (total_net - refund_net), precision_digits=2, rounding_method='UP')
                val['whvat'] = float_round(
                    (withholding), precision_digits=2, rounding_method='UP') * type_

                val['amt'] = doc.amount_total * type_
                val['total'] = doc.amount_residual * type_

                total += doc.amount_residual * type_
                total_paid += doc.amount_total - doc.amount_residual * type_

                if doc.partner_id.id in data:
                    data[doc.partner_id.id]['vals'].append(val)
                    data[doc.partner_id.id]['wh'] += withholding
                    data[doc.partner_id.id]['total'] += total
                    data[doc.partner_id.id]['total_paid'] += total_paid
                else:
                    data[doc.partner_id.id] = {}
                    data[doc.partner_id.id]['vendor'] = doc.partner_id.name
                    data[doc.partner_id.id]['vendor_pin'] = doc.partner_id.vat
                    data[doc.partner_id.id]['vals'] = [val]
                    data[doc.partner_id.id]['wh'] = withholding
                    data[doc.partner_id.id]['total'] = total
                    data[doc.partner_id.id]['total_paid'] = total_paid

            # refunds = self.env['account.move'].search([
            #     ('partner_id', '=', doc.partner_id.id), ('move_type', '=', 'in_refund'),
            #     ('state', 'not in', ['cancel', 'paid', 'draft']), ('origin', 'not ilike', 'BILL/')])
            refunds = self.env['account.move'].search([
                ('partner_id', '=', doc.partner_id.id), ('move_type', '=', 'in_refund'),
                ('state', 'not in', ['cancel', 'paid', 'draft'])])

            for refund in refunds:
                if refund.partner_id.id in data:
                    desc = [line.name for line in max(
                        refund.invoice_line_ids, key=lambda x: x.price_subtotal)]

                    data[refund.partner_id.id]['vals'].append({
                        'net': refund.amount_untaxed * -1,
                        'vat': refund.amount_tax * -1,
                        # # ================================HERE==============
                        # 'whvat': sum(refund.tax_line_ids.filtered(
                        #     lambda r: r.amount < 0).mapped('amount')),
                        # # ================================HERE==============
                        'whvat': refund._compute_wht_tax(),
                        'non_vat': 0,
                        'paid': '',
                        'amt': refund.amount_total * -1,
                        'total': refund.amount_total * -1,
                        # 'inv': refund.ven_inv_no,
                        'date': refund.invoice_date.strftime('%d/%m/%Y'),
                        'description': refund.name
                    })

        for i in data:
            data[i]['totals'] = {'net': 0, 'vat': 0, 'amt': 0,
                                 'non_vat': 0, 'whvat': 0, 'total': 0}
            for j in data[i]:
                if j == 'vals':
                    for k in data[i][j]:
                        data[i]['totals']['net'] += k['net']
                        data[i]['totals']['vat'] += k['vat']
                        data[i]['totals']['non_vat'] += k['non_vat']
                        data[i]['totals']['whvat'] += k['whvat']
                        data[i]['totals']['amt'] += k['amt']
                        data[i]['totals']['total'] += k['total']

        return {
            'docs': docs,
            'data': data,
        }
