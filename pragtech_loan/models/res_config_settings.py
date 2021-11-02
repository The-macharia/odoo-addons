# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    loan_approval = fields.Boolean("Loan Approval")
    validation_amount = fields.Monetary(string="Minimum Amount", currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')
#     company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
#         help='Utility field to express amount currency')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            loan_approval = self.env['ir.config_parameter'].sudo().get_param('pragtech_loan.loan_approval'),
            validation_amount = float(self.env['ir.config_parameter'].sudo().get_param('pragtech_loan.validation_amount')),
            company_currency_id = int(self.env['ir.config_parameter'].sudo().get_param('pragtech_loan.company_currency_id.id'))
           )
        return res

    #@api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pragtech_loan.loan_approval', self.loan_approval)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_loan.validation_amount', self.validation_amount)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_loan.company_currency_id', self.company_currency_id)

