from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    commission = fields.Monetary(
        string='Commission', readonly=True, help="Value calculated from Newmatic sales commission.")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super().action_payslip_done()
        for rec in self:
            rec.contract_id.commission = 0

        return res
