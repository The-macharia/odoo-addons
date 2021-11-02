from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools.misc import formatLang
import json

class Loan(models.Model):
    _inherit = 'account.loan'
    
    gender = fields.Selection(related='partner_id.gender', string="Gender", store=True)
    business_industry_id = fields.Many2one(related='partner_id.business_industry_id', string="Industry", store=True)

class account_loan_dashboard(models.Model):
    _inherit = 'account.loan.dashboard'
    
    ##get gender wize loans
    def _get_gender_count(self):
        cur_id = None
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial','approved','done']),('company_id','=',self.env.user.company_id.id)])
            cur_id = self.env.user.company_id.currency_id
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial','approved','done'])])
            cur_id = self.env.user.company_id.currency_id
        male_cnt = 0 
        female_cnt = 0
        undefined_cnt = 0
        total_male = 0.00
        total_female = 0.00
        total_undefined = 0.00
        for loan in loan_obj:
            if loan.partner_id.gender == 'male':
                male_cnt += 1
                for dis in loan.disbursement_details:
                    total_male += dis.disbursement_amt
            elif loan.partner_id.gender == 'female':
                female_cnt += 1
                for dis in loan.disbursement_details:
                    total_female += dis.disbursement_amt
            else:
                undefined_cnt +=1
                for dis in loan.disbursement_details:
                    total_undefined += dis.disbursement_amt
                
        self.male_loan_count = male_cnt
        self.female_loan_count = female_cnt
        self.undefined_loan_count = undefined_cnt
        if cur_id:
            self.male_loan_total = formatLang(self.env, cur_id.round(total_male) + 0.0, currency_obj=cur_id)
            self.female_loan_total = formatLang(self.env, cur_id.round(total_female) + 0.0, currency_obj=cur_id)
            self.undefined_loan_total = formatLang(self.env, cur_id.round(total_undefined) + 0.0, currency_obj=cur_id)
        else:
            self.male_loan_total = 0.00
            self.female_loan_total = 0.00
            self.undefined_loan_total = 0.00
            
            
            
    def get_gender_details(self):
        cur_id = None
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state','in',['partial','approved','done']),('company_id','=',self.env.user.company_id.id)])
            cur_id = self.env.user.company_id.currency_id
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state','in',['partial','approved','done'])])
            cur_id = self.env.user.company_id.currency_id
        total_male = 0.00
        total_female = 0.00
        total_undefined = 0.00
        all_loan_total = 0.00
        for loan in loan_obj:
            if loan.partner_id.gender == 'male':
                for dis in loan.disbursement_details:
                    total_male += dis.disbursement_amt
                    all_loan_total += dis.disbursement_amt
            elif loan.partner_id.gender == 'female':
                for dis in loan.disbursement_details:
                    total_female += dis.disbursement_amt
                    all_loan_total += dis.disbursement_amt
            else:
                for dis in loan.disbursement_details:
                    total_undefined += dis.disbursement_amt
                    all_loan_total += dis.disbursement_amt
#         if cur_id:
#             male_total = formatLang(self.env, cur_id.round(total_male) + 0.0, currency_obj=cur_id)
#             female_total = formatLang(self.env, cur_id.round(total_female) + 0.0, currency_obj=cur_id)
#             undefined_total = formatLang(self.env, cur_id.round(total_undefined) + 0.0, currency_obj=cur_id)
#         else:
#             male_total = 0.00
#             female_total = 0.00
#             undefined_total = 0.00

            
            
        return {'male':total_male,'female':total_female, 'undefined': total_undefined, 'all_loan':all_loan_total}
    
    #@api.multi
    def get_gender_info(self):
        '''
            Called from Compute method to calculate data for gender(women) 
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        amount = self.get_gender_details()
        
        data = [
                {'value': amount['male'], 'label':'Male'},
                {'value': amount['female'], 'label': 'Female'},
                {'value': amount['undefined'], 'label': 'Undefined'}
                ]
        return [{'values': data, 'title': '', 'key': _('Women owners')}]
    
    def _gender_graph_detail(self):
        self.gender_graph_detail = json.dumps(self.get_gender_info())
        
    def _get_female_percent(self):
        '''
            a compute method that calculates the gender percentage and assigns 
            to delinquency_percent
            params : self
        '''
        gen = self.get_gender_details()
        for rec in self:
            try:
                rec.get_female_percent = round((float(gen['female'])/float(gen['all_loan']))*100,2)
                rec.get_male_percent = round((float(gen['male'])/float(gen['all_loan']))*100,2)
            except ZeroDivisionError:
                rec.get_female_percent = 0
                rec.get_male_percent = 0
            
        
    male_loan_count = fields.Integer(compute="_get_gender_count")
    female_loan_count = fields.Integer(compute="_get_gender_count")
    undefined_loan_count = fields.Integer(compute="_get_gender_count")
    male_loan_total = fields.Char(compute="_get_gender_count")
    female_loan_total = fields.Char(compute="_get_gender_count")
    undefined_loan_total = fields.Char(compute="_get_gender_count")
    gender_graph_detail = fields.Text(compute='_gender_graph_detail')
    get_female_percent = fields.Float(compute='_get_female_percent')
    get_male_percent = fields.Float(compute='_get_female_percent')
    
