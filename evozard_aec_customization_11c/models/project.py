from openerp import models, fields, api
from openerp.tools.translate import _


class Project(models.Model):
    _inherit = 'project.project'
    
    service_start_date= fields.Date('Service Start Date')
    service_end_date= fields.Date('Service End Date')
    
    district = fields.Char(related='partner_id.district', string='District', store=True)
    nationality_id = fields.Many2one(related='partner_id.nationality_id', relation='res.country', string='Nationality', store=True)
    industry_id = fields.Many2one(related='partner_id.business_industry_id', relation='business.industry', string='Industry', store=True)
    credit_status_id = fields.Many2one(related='partner_id.credit_status_id', relation='credit.status', string='Payment Status', store=True)
    business_stage_id = fields.Many2one(related='partner_id.business_stage_id', relation='business.stage', string='Contract Status', store=True)
    gender = fields.Selection(related='partner_id.gender', selection=[('male','Male'), ('female','Female')], string='Gender of Ownership', store=True)
    full_time_employees = fields.Integer(related='partner_id.full_time_employees', string='Jobs Created - Full Time', store=True)
    casual_employees= fields.Integer(related='partner_id.casual_employees', string='Jobs Created - Part Time', store=True)
    other_employees = fields.Integer(related='partner_id.other_employees', string='Jobs Created - Casual', store=True)
    growth_revenue = fields.Monetary(related='partner_id.growth_revenue', string='Growth in Revenue', store=True)
    application_status_id = fields.Many2one(related='partner_id.application_status_id', relation='loan.application.status', string='Loan Application Status', store=True)
    loan_status_id = fields.Many2one(related='partner_id.loan_status_id', relation='loan.status', string='Loan Status', store=True)
    aec_loan_amt = fields.Monetary(related='partner_id.aec_loan_amt', string='AEC Loan Amount', store=True)
    ext_loan_amt = fields.Monetary(related='partner_id.ext_loan_amt', string='External Loan Amount', store=True)
    start_date = fields.Date(related='partner_id.start_date', string='Loan Start Date', store=True)
    end_date = fields.Date(related='partner_id.end_date', string='Loan End Date', store=True)
#     user_id = fields.Many2one(related='partner_id.user_id', relation='res.users', string='Salesperson', index=True, track_visibility='onchange', default=lambda self: self.env.user, store=True)
    lead_source_id = fields.Many2one(related='partner_id.lead_source_id', relation='lead.source', string='Lead Partner Source', store=True)
    
