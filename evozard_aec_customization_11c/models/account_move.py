from odoo import api, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    #@api.one
    def _prepare_analytic_line(self):
        if not self.name:
            default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
            self.name = default_name
        res = super(AccountMoveLine, self)._prepare_analytic_line()
        if res:
            return res[0]
        return super(AccountMoveLine, self)._prepare_analytic_line()
        
            
    
    