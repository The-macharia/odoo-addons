from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime

class Province(models.Model):
    _name = 'res.country.province'
    
    name = fields.Char(string="Province Name")
    
    
class Sector(models.Model):
    _name = 'res.country.sector'
    
    name = fields.Char(string="Sector Name")
    
class Cell(models.Model):
    _name = 'res.country.cell'
    
    name = fields.Char(string="Cell Name")
    
    
class Partner(models.Model):
    _inherit = 'res.partner'
    
    def write(self, vals):
        if vals.get('name'):
            if not self.env.user.has_group('aec_partner_extension.can_edit_name'):
                raise UserError(_("You Don't Have Access To Change The Customer's Name.\nPlease Contact Your System Administrator."))
        
        return super(Partner,self).write(vals)
    
    @api.depends('intro_bcm_training', 'dbc_training','bktt_training','cash_flow_inv_mgt','db_in_rwanda','cn_days','taxation','marketing','finance_fr_growth')
    def _compute_training_attended(self):
        for record in self:
            count = 0
            print("Self-----",self)
            if record.intro_bcm_training:
                count += 1
            if record.dbc_training:
                count += 1
            if record.bktt_training:
                count += 1
            if record.cash_flow_inv_mgt:
                count += 1
            if record.db_in_rwanda:
                count += 1
            if record.cn_days:
                count += 1
            if record.taxation:
                count += 1
            if record.marketing:
                count += 1
            if record.finance_fr_growth:
                count += 1
            record.training_attend = count
            
    @api.depends('baseline','end_line', 'first_folloup', 'second_folloup','third_folloup')
    def _compute_evalue_sample(self):
        for record in self:
            count = 0
            if record.baseline:
                count += 1
            if record.end_line:
                count += 1
            if record.first_folloup:
                count += 1
            if record.second_folloup:
                count += 1
            if record.third_folloup:
                count += 1
            record.evalue_sample = count
            
                
    province_id = fields.Many2one('res.country.province', string="Province")
    sector_id = fields.Many2one('res.country.sector', string="Sector")
    cell_id = fields.Many2one('res.country.cell')
    dist = fields.Char("District")
    village = fields.Char("Village")
    Plot = fields.Char("Plot")
    
    program_type = fields.Selection([('lt','LT'),('fp','FP')], string="Program Type")
    training_attend = fields.Char(string="Training Attended",compute='_compute_training_attended')
    educational_id = fields.Many2one('educational.level', string="Educational Level")
    registration_id = fields.Many2one('business.registration.status', string="Business Registration Status")
    year_of_opr = fields.Integer(string="Year Of Operation")
    bus_gen_opr = fields.Selection([('yes','Yes'),('no','No')], string="Business Operating and Generating Revenue")
    business_nature = fields.Selection([('products','Products'),('services','Services')], string="Business Nature")
    no_of_emp = fields.Char(string="Number or Employees")
    fina_book_kep = fields.Selection([('yes','Yes'),('no','No')], string = "Do you keep financial records? ")
    lst_year_revenue = fields.Integer(string="Monthly Revenue")
    camp_id = fields.Many2one('camp.details', string="Camp / Location")
    intro_bcm_training = fields.Boolean(string="Intro +BCM Training")
    dbc_training = fields.Boolean(string="Day Boot Camp")
    bktt_training = fields.Boolean(string="Book Keeping Tool training")
    cash_flow_inv_mgt = fields.Boolean(string="CashFlow and Inventory Management")
    db_in_rwanda = fields.Boolean(string="Doing Business in Rwanda")
    cn_days = fields.Boolean(string="Community Network Days")
    taxation = fields.Boolean(string="Taxation")
    marketing = fields.Boolean(string="Marketing")
    finance_fr_growth = fields.Boolean(string="Financing for Growth")
    inkomoko = fields.Integer(stirng="How many years have you worked with Inkomoko?")
    ft_fp_reco = fields.Selection([('lt','LT'),('fp','FP')],string="LT or FP Recommendation")
    cohort_registration_year = fields.Many2many('res.year', 'partner_id', 'year_id', string="Cohort / Registration year")
    
    baseline = fields.Boolean(string="Baseline")
    end_line = fields.Boolean(string="End-Line")
    first_folloup = fields.Boolean(string="First Follow-up")
    second_folloup = fields.Boolean(string="Second Follow-up")
    third_folloup = fields.Boolean(string="Third Follow-up")
    evalue_sample = fields.Char(string="Evaluation Sample",compute='_compute_evalue_sample')
    block = fields.Char(string="Block",help="this is only available for kenya country")

    @api.onchange('cohort_registration_year')
    def onchange_cohort_registration_year(self):
        now = datetime.datetime.now()
        current_year = now.year
        year_lst = []
        if current_year:
            year_before_twenty_years = current_year - 50
            if year_before_twenty_years:
                for year in range(year_before_twenty_years,current_year+1):
                    year_id = self.env['res.year'].search([('name', '=', str(year))])
                    if year_id:
                        year_lst.append(year_id.id)
                    if not year_id:
                        created_year_id = self.env['res.year'].create({'name':year})
                        year_lst.append(created_year_id.id)
        return {'domain':{'cohort_registration_year':[('id', 'in', year_lst)]}} 
    
        
class res_year(models.Model):
    _name = 'res.year'
    _order = "id desc"
    
    name = fields.Char(string="Year")
    
    
    
    
    
     
    
    