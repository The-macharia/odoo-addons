from openerp import models, fields, api
from openerp.tools.translate import _


class res_partner_fields(models.Model):
    _inherit = 'res.partner'
    
    lead_source_id = fields.Many2one('lead.source', string='Lead Partner Source')
    referal_contact_id = fields.Many2one('res.partner', string='Lead Referal Contact')
    source_type_id = fields.Many2one('source.type', string='Lead Source Type')
    district = fields.Char('District')
    id_no = fields.Char('ID Number')
    business_industry_id = fields.Many2one(
        'res.partner.industry', string='Industry')
    # business_industry_id = fields.Many2one('business.industry', string='Industry')
    business_operating_status_id = fields.Many2one('business.operating.status', string='Business Operating Status')
    business_description = fields.Text('Business Description')
    business_stage_id = fields.Many2one('business.stage', string='Contract Status')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender of Ownership')
    credit_check_details = fields.Text('Customer Credit Check Details')
    credit_status_id = fields.Many2one('credit.status', 'Payment Status')
    revenue_level_id = fields.Many2one('revenue.level', 'Revenue Level')
    full_time_employees = fields.Integer('Jobs Created - Full Time')
    casual_employees= fields.Integer('Jobs Created - Part Time')
    other_employees = fields.Integer('Jobs Created - Casual')
    nationality_id = fields.Many2one('res.country', string='Nationality')
    account_manager_id = fields.Many2one('res.users', string='Account Manager')
    application_status_id = fields.Many2one('loan.application.status', string='Loan Application Status')
    loan_status_id = fields.Many2one('loan.status', string='Loan Status')
    start_date = fields.Date('Loan Start Date')
    end_date = fields.Date('Loan End Date')
    growth_revenue = fields.Monetary('Growth in Revenue')
    aec_loan_amt = fields.Monetary('AEC Loan Amount')
    ext_loan_amt = fields.Monetary('External Loan Amount')
    

class RevenueLevel(models.Model):
    _name = 'revenue.level'
    
    name = fields.Char("Name", required=True)
    
    
class BusinessIndustry(models.Model):
    _name = 'business.industry'
    
    name = fields.Char("Name", required=True)
    
    
class BusinessOperatingStatus(models.Model):
    _name = 'business.operating.status'
    
    name = fields.Char("Name", required=True)
    

class BusinessStage(models.Model):
    _name = 'business.stage'
    
    name = fields.Char("Name",required=True)


class CreditCheckStatus(models.Model):
    _name = 'credit.status'
    
    name = fields.Char("Name",required=True)


class LoanApplicationStatus(models.Model):
    _name = 'loan.application.status'
    
    name = fields.Char("Name",required=True)
    

class LoanStatus(models.Model):
    _name = 'loan.status'
    
    name = fields.Char("Name",required=True)


class SourceType(models.Model):
    _name = 'source.type'
    
    name = fields.Char("Name",required=True)


class LeadSource(models.Model):
    _name = 'lead.source'
    
    name = fields.Char("Name",required=True)
