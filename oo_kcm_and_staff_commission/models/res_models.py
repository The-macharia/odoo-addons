from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].set_param(
            'kcm_and_staff_commission.kcm_tax_id', int(self.kcm_tax_id.id))

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPsudo = self.env['ir.config_parameter'].sudo()

        res.update(
            kcm_tax_id=int(ICPsudo.get_param(
                'kcm_and_staff_commission.kcm_tax_id'))
        )
        return res

    kcm_tax_id = fields.Many2one('account.tax', string="KCM Tax")
