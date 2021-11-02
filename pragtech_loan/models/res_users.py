from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    loan_disbursement_limit = fields.Float()
    
    def get_logged_name(self):
        user = self.env['res.users'].browse(self._context.get('uid'))
        name = ''
        if user:
            name = user.partner_id.display_name if user.partner_id else user.name
        return name
        