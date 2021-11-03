from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_line(self):
        for rec in self:
            if not rec.name:
                default_name = rec.name or (
                    rec.ref or '/' + ' -- ' + (rec.partner_id and rec.partner_id.name or '/'))
                rec.name = default_name
            res = super(AccountMoveLine, rec)._prepare_analytic_line()
            if res:
                return res[0]
            return super(AccountMoveLine, rec)._prepare_analytic_line()
