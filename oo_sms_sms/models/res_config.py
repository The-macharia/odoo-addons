# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_sms_api = fields.Boolean(
        string="Enable SMS", config_parameter='oo_sms_sms.enable_sms_api')
    sms_username = fields.Char(
        string='Username', default='sandbox',
        config_parameter='oo_sms_sms.sms_username')
    sms_api_key = fields.Char(
        string='Api Key', config_parameter='oo_sms_sms.sms_api_key')
    sms_shortcode = fields.Char(
        string="Shortcode", size=5, config_parameter='oo_sms_sms.sms_shortcode')
    sales_enaled = fields.Boolean(
        string='Enable Sales SMS', config_parameter='oo_sms_sms.sales_enaled')
    sale_sms_template_id = fields.Many2one(
        'sms.template', string='Sales SMS Template', config_parameter='oo_sms_sms.sale_sms_template_id')
    invoice_enabled = fields.Boolean(
        string='Enable Customer Invoices SMS', config_parameter='oo_sms_sms.invoice_enabled')
    invoice_sms_template_id = fields.Many2one(
        'sms.template', string='Invoice SMS Template', config_parameter='oo_sms_sms.invoice_sms_template_id')
    purchase_enabled = fields.Boolean(
        string='Enable Purchase SMS', config_parameter='oo_sms_sms.purchase_enabled')
    purchase_sms_template_id = fields.Many2one(
        'sms.template', string='Purchase SMS Template', config_parameter='oo_sms_sms.purchase_sms_template_id')
    payment_enabled = fields.Boolean(
        string='Enable Payment SMS', config_parameter='oo_sms_sms.payment_enabled')
    payment_sms_template_id = fields.Many2one(
        'sms.template', string='Payments SMS Template', config_parameter='oo_sms_sms.payment_sms_template_id')
