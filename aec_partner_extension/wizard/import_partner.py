from odoo import api, fields, models, _
import base64
import xlrd
from odoo.exceptions import Warning


class ImportPartner(models.TransientModel):
    
    _name = 'import.partner'
    
    name = fields.Char('Partner Import', default='Import Partner', readonly=True) 
    actual_file = fields.Binary(string='Upload File',)
    
    def import_partner(self):
        
        if not self.actual_file:
            raise Warning(_("Please Upload the file."))
            
        actual_csv_data = base64.decodestring(self.actual_file)
        if actual_csv_data:
            try:
                book = xlrd.open_workbook(file_contents=actual_csv_data)
            except:
                raise Warning(_('Incorrect File Format!'))
            
            try:
                first_sheet = book.sheet_by_index(0)
                vals = {}
                for n in range(1, first_sheet.nrows):
                    data = first_sheet.row_values(n)
                    id_no = data[0] if data[0] else ''
                    
                    camp = ''
                    sat = ''
                    pro = ''
                    sec = ''
                    cell = ''
                    country = ''
                    comm = ''
                    nat = ''
                    ind = ''
                    stat = ''
                    stage = ''
                    edu = ''
                    lead_source = ''
                    contract_status = ''
                    if id_no:
                        if data[1]:
                            camp = self.env['camp.details'].search([('name', '=', data[1])], limit=1)
                            if not camp:
                                raise Warning('Camp not available with name of {}'.format(data[1]))
                        camp_id = camp.id if camp else None
                        
                        name = data[2] if data[2] else 'Unknown'
                        is_customer = data[3] or False
                        company_type = 'company' if data[4] else 'person'
                        is_group = data[5] if data[5] else False
                        street = data[6] if data[6] else ''
                        street2 = data[7] if data[7] else ''
                        city = data[8] if data[8] else ''
                        if data[9]:
                            sat = self.env['res.country.state'].search([('name', '=', data[9])], limit=1)
                            if not sat:
                                raise Warning('State not available with name of {}'.format(data[9])) 
                        state = sat.id if sat else None
                        if data[10]:
                            pro = self.env['res.country.province'].search([('name', '=', data[10])], limit=1)
                            if not pro:
                                raise Warning('Province not available with name of {}'.format(data[10])) 
                        province_id = pro.id if pro else None
                        if data[11]:
                            sec = self.env['res.country.sector'].search([('name', '=', data[11])], limit=1)
                            if not sec:
                                raise Warning('Sector not available with name of {}'.format(data[11]))
                        sector_id = sec.id if sec else None
                        if data[12]:
                            cell = self.env['res.country.cell'].search([('name', '=', data[12])], limit=1)
                            if not cell:
                                raise Warning('Cell not available with name of {}'.format(data[12]))
                        cell_id = cell.id if cell else None
                        village = data[13] if data[13] else ''
                        plot = data[14] if data[14] else ''
                        district = data[15] if data[15] else ''
                        if data[16]:
                            country = self.env['res.country'].search([('name', '=', data[16])], limit=1) 
                            if not country:
                                raise Warning('Country not available with name of {}'.format(data[16]))
                        country_id = country.id if country else None
                        if data[17]:
                            comm = self.env['res.country'].search([('name', '=', data[17])], limit=1)
                            if not comm:
                                raise Warning('Country not available with name of {}'.format(data[17]))
                        commercial_partner_country_id = comm.id if comm else None
                        zip1 = data[18] if data[18] else ''
                        email = data[19] if data[19] else ''
                        website = data[20] if data[20] else ''
                        mobile = data[21] if data[21] else ''
                        phone = data[22] if data[22] else ''
                        business_description = data[23] if data[23] else ''
                        credit_check_details = data[24] if data[24] else ''
                        if data[25]:
                            nat = self.env['res.country'].search([('name', '=', data[25])], limit=1) 
                            if not nat:
                                raise Warning('Country not available with name of {}'.format(data[25]))
                        nationality_id = nat.id if nat else None
                        if data[26]:
                            ind = self.env['business.industry'].search([('name', '=', data[26])], limit=1) 
                            if not ind:
                                raise Warning('Industry not available with name of {}'.format(data[26]))
                        business_industry_id = ind.id if ind else None
                        if data[27]:
                            stat = self.env['credit.status'].search([('name', '=', data[27])], limit=1)
                            if not stat:
                                raise Warning('Credit status not available with name of {}'.format(data[27]))
                        credit_status_id = stat.id if stat else None
                        if data[28]:
                            stage = self.env['business.stage'].search([('name', '=', data[28])], limit=1)
                            if not stage:
                                raise Warning('Stage not available with name of {}'.format(data[28])) 
                        business_stage_id = stage.id if stage else None
                        full_time_employees = data[29] if data[29] else 0
                        casual_employees = data[30] if data[30] else 0
                        other_employees = data[31] if data[31] else 0
                        growth_revenue = data[32] if data[32] else ''
                        gender = data[33].lower() if data[33].lower() else False
                        program_type = data[34].lower() if data[34].lower() else None
                        if data[35]:
                            edu = self.env['educational.level'].search([('name', '=', data[35])], limit=1)
                            if not edu:
                                raise Warning('Educational level not available with name of {}'.format(data[35]))
                        educational_id = edu.id if edu else None
                        bus_gen_opr = data[36].lower() if data[36].lower() else False
                        year_of_opr = data[37] if data[37] else ''
                        business_nature = data[38].lower() if data[38].lower() else False
                        no_of_emp = data[39] if data[39] else 0
                        fina_book_kep = data[40] if data[40] else ''
                        lst_year_revenue = data[41] if data[41] else 0
                        inkomoko = data[42] if data[42] else 0
                        ft_fp_reco = data[43].lower() if data[43].lower() else False
                        
                        comment = data[45] if data[45] else ''
                        intro_bcm_training = data[46] if data[46] else False
                        bktt_training = data[47] if data[47] else False
                        
                        db_in_rwanda = data[48] if data[48] else False
                        taxation = data[49] if data[49] else False
                        finance_fr_growth = data[50] if data[50] else False
                        dbc_training = data[51] if data[51] else False
                        cash_flow_inv_mgt = data[52] if data[52] else False
                        cn_days = data[53] if data[53] else False
                        marketing = data[54] if data[54] else False
                        baseline = data[55] if data[55] else False
                        end_line = data[56] if data[56] else False
                        first_folloup = data[57] if data[57] else False
                        second_folloup = data[58] if data[58] else False
                        third_folloup = data[59] if data[59] else False 
                         
                        if data[60]:
                            lead_source = self.env['lead.source'].search([('name', '=', data[60])], limit=1) 
                            if not lead_source:
                                raise Warning('Lead Partner Source not available with name of {}'.format(data[60]))
                            
                        lead_source_id = lead_source.id if lead_source else None
                            
                        if data[61]:
                            contract_status = self.env['business.stage'].search([('name', '=', data[61])], limit=1) 
                            if not contract_status:
                                raise Warning('Contract Status not available with name of {}'.format(data[61])) 
                        contract_status_id = contract_status.id if contract_status else None         
                        
    #                     years = str(data[44])[1:].split(',')
                        year_ids = []
                        if data[44]:
                            years = str(data[44]).split(',')
                            
                            for year in years:
                                year_record = self.env['res.year'].search([('name', '=', year)])
                                if year_record:
                                    year_ids.append(year_record.id)
                        cohort_registration_year = [(6, 0, year_ids)] if year_ids else None
                        
                        vals = {
                            'id_no':id_no, 'name':name, 'camp_id':camp_id, 'customer':is_customer,
                            'company_type':company_type, 'is_group':is_group,
                            'street':street, 'street2':street2, 'city':city, 'state_id':state,
                            'province_id':province_id, 'sector_id':sector_id, 'cell_id':cell_id,
                            'village':village, 'Plot':plot, 'district':district, 'country_id':country_id,
    #                         'commercial_partner_country_id':commercial_partner_country_id,
                            'zip':zip1, 'email':email, 'website':website, 'mobile':mobile, 'phone':phone,
                            'business_description':business_description, 'credit_check_details':credit_check_details,
                            'nationality_id':nationality_id, 'business_industry_id':business_industry_id,
                            'business_stage_id':business_stage_id, 'full_time_employees':full_time_employees,
                            'casual_employees':casual_employees, 'other_employees':other_employees,
                            'credit_status_id':credit_status_id,
                            'growth_revenue':growth_revenue, 'gender':gender, 'program_type':program_type,
                            'educational_id':educational_id, 'bus_gen_opr':bus_gen_opr, 'year_of_opr':year_of_opr,
                            'business_nature':business_nature, 'no_of_emp':no_of_emp, 'fina_book_kep':fina_book_kep,
                            'lst_year_revenue':lst_year_revenue, 'inkomoko':inkomoko, 'ft_fp_reco':ft_fp_reco,
                            'cohort_registration_year':cohort_registration_year,
                            'comment':comment, 'intro_bcm_training':intro_bcm_training, 'bktt_training':bktt_training,
                            'db_in_rwanda':db_in_rwanda, 'taxation':taxation, 'finance_fr_growth':finance_fr_growth,
                            'dbc_training':dbc_training, 'cash_flow_inv_mgt':cash_flow_inv_mgt, 'cn_days':cn_days,
                            'marketing':marketing, 'baseline':baseline, 'end_line':end_line,
                            'first_folloup':first_folloup, 'second_folloup':second_folloup, 'third_folloup':third_folloup,
                            'lead_source_id':lead_source_id,'business_stage_id':contract_status_id
                            }
                        
                        customer = self.env['res.partner'].search([('id_no', '=', id_no)])
                        if customer:
                            customer.write(vals)
                        else:
                            customer.create(vals)
            except Exception as e:
                raise Warning(_(e))
                    
    
