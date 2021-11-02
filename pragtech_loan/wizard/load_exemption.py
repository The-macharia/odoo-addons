from odoo import fields, models, api, _

class LoanExtended(models.TransientModel):
    _name = "load.exemption"
    _description = "loan"

    #@api.multi
    def update_tax_loan(self):
        loan_id = self.env['account.loan'].browse(self._context['active_ids'])
        for loan in loan_id:
            for insatllment in loan.installment_id:
                if insatllment.state == 'draft' and insatllment.fee_lines:
                    for tax_id in insatllment.fee_lines:
                        if tax_id.tax > 0:
                            tax_id.base = tax_id.base + tax_id.tax
                            tax_id.tax = 0.0

                if  insatllment.state == 'open' and insatllment.fee_lines:
                    for tax_id in insatllment.fee_lines:
                        if tax_id.tax > 0:
                            tax_id.base = tax_id.base + tax_id.tax
                            tax_id.tax = 0.0

                        if tax_id.tax_paid > 0:
                            tax_id.base_paid = tax_id.base_paid + tax_id.tax_paid
                            tax_id.tax_paid = 0.0







