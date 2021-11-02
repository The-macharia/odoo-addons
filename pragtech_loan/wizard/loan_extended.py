from odoo import fields, models, api, _
from odoo.exceptions import UserError, Warning
import datetime

class LoanExtended(models.TransientModel):
    _name = "loan.extended"
    _description = "Extended loan period"

    date = fields.Date('Date', default=fields.Date.today())
    period_id = fields.Many2one('loan.installment.period', 'Loan Period')
    grc_period = fields.Many2one('loan.installment.period', 'Grace Period')
    loan_extension = fields.Boolean(default=True)
    gp_with_no_extension = fields.Boolean(string="Grace Period With No Extension")
    gp_with_extension = fields.Boolean(string="Grace Period With Extension")
    installment_id = fields.Many2one('account.loan.installment', string="Installment")
#     payment_freq = fields.Char("Payment Frequency")
#     @api.model
#     def default_get(self, fields):
#         
#         res = super(LoanExtended, self).default_get(fields)
#         active_id = self._context.get('active_id')
#         acc_loan = self.env['account.loan'].browse(active_id)
#         res.update({
#             'payment_freq': acc_loan.payment_freq,
#           })
#         return res
    
#     @api.onchange('payment_freq')
#     def onchange_payment_freq(self):
#         if self.payment_freq == 'quarterly':
#             period_ids = self.env['loan.installment.period'].search([])
#             freq_ids = []
#             for o in period_ids:
#                 if o.period and o.period % 3 == 0:
#                     freq_ids.append(o.id)
#             return {'domain':{'grc_period':[('id', 'in', freq_ids)]}}
        
#     @api.onchange('loan_extension')
#     def onchange_loan_extension(self):
#         if self.loan_extension:
#             loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
#             installment_line = self.env['account.loan.installment']
#             original_list = installment_line.search([('loan_id', '=', loan_id.id),('state', '=', 'draft')]).ids
#             remove_list = installment_line.search([('loan_id', '=', loan_id.id),('state', '=', 'draft'), ('late_fee', '!=', 0.0)]).ids
#             res = [i for i in original_list if i not in remove_list] 
#             return {'domain':{'installment_id':[('id', 'in', res)]}}
            
    @api.onchange('gp_with_no_extension')
    def onchange_with_no_extenstion(self):
        if self.gp_with_no_extension:
            self.loan_extension = False
            self.gp_with_extension = False
            self.grc_period = False
            self.installment_id = False
            
    @api.onchange('loan_extension')
    def onchange_extenstion(self):
        if self.loan_extension:
            self.gp_with_no_extension = False
            self.gp_with_extension = False
            self.grc_period = False
            self.installment_id = False
            
    @api.onchange('gp_with_extension')
    def onchange_with_extenstion(self):
        if self.gp_with_extension:
            self.gp_with_no_extension = False
            self.loan_extension = False
            self.grc_period = False
            self.installment_id = False
            
    def get_last_installment_number(self, last_installment_no):
        ins_num = ""
        flag = True
        cnt = 1
        if last_installment_no:
            while flag:
                flag = last_installment_no[-cnt].isdigit()
                if flag == True:
                    ins_num += last_installment_no[-cnt]
                cnt += 1
        ins_num = ins_num[::-1]
        if not ins_num.isdigit():
            raise Warning("Please Check Installment Name")
        return int(ins_num)
    ##loan extension with existed installment line ........
    def update_existed_line_with_extension(self, prin_amt, int_amt, fees_amt, late_fees):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        drft_line = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id),('state', '=', 'draft')])
        tot_draft = 0
        if drft_line:
            tot_draft = len(drft_line)
        if tot_draft:
            if prin_amt:
                prin_amt = prin_amt / tot_draft
            if int_amt:
                int_amt = int_amt / tot_draft
            if fees_amt:
                fees_amt = fees_amt / tot_draft
            if late_fees:
                late_fees = late_fees / tot_draft
        for line in drft_line:
            if prin_amt:
                line.write({'capital':line.capital + prin_amt,'outstanding_prin':line.outstanding_prin + prin_amt})
            if int_amt:
                line.write({'interest':line.interest + int_amt, 'outstanding_int':line.outstanding_int + int_amt})
            if fees_amt:
                line.write({'fees':line.fees + fees_amt, 'outstanding_fees':line.outstanding_fees + fees_amt})
                for fee_line in line.fee_lines:
                    if fee_line.name == 'fees':
                        fee_line.write({'base':fee_line.base + fees_amt})
            if late_fees:
                line.write({'late_fee':line.late_fee + late_fees})
                search_ids = self.env['fees.lines'].search([('name', '=', 'late_fee'),('installment_id','=',line.id)])
                if search_ids:
                    for fee_line in search_ids:
                        if fee_line.name == 'late_fee':
                            fee_line.write({'base':fee_line.base + late_fees})
                else:
                    late_fee_product_id = False
                    for com_line in loan_id.loan_type.loan_component_ids:
                        if com_line.type == 'late_fee':
                            late_fee_product_id = com_line.product_id
                    if late_fee_product_id:
                        fees_line_vals = {
                                'name':'late_fee',
                                'product_id':late_fee_product_id.id,
                                'base':late_fees,
                                'installment_id':line.id
                                }
                        self.env['fees.lines'].create(fees_line_vals)
            line.write({'total':line.total + (prin_amt + int_amt + fees_amt)})
        paid_line = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id),('state', 'in', ['paid'])])
        for pl in paid_line:
            pl.due_principal = 0.0
            pl.due_interest = 0.0
            pl.due_fees = 0.0
            pl.installment_due = 0.0
            
    ##loan extension with new installment lines forwarded loan for given period ..........       
    def create_new_installment(self, line, ins_num, ins_date):
        installment_vals = {'name':'installment' + str(ins_num),\
                                    'date':ins_date, 'loan_id':line.loan_id.id,\
                                    'capital':line.capital, 'interest':line.interest,'fees':line.fees,\
                                    'total':line.total, 'partner_id':line.loan_id.partner_id.id,\
                                     'outstanding_prin':line.outstanding_prin,'outstanding_int':line.outstanding_int,\
                                     'outstanding_fees':line.outstanding_fees,
                                     'late_fee':line.late_fee
                                     }
        line_id = self.env['account.loan.installment'].create(installment_vals)
        if line_id:
            for fee_line in line.fee_lines:
                fees_line_vals = {
                                    'name':fee_line.name,
                                    'product_id':fee_line.product_id.id,
                                    'base':fee_line.base,
                                    'tax':fee_line.tax,
                                    'installment_id':line_id.id
                                    }
                self.env['fees.lines'].create(fees_line_vals)
        return line_id
    ##loan extension with grace period ..............
    def add_existed_installment(self, installments, cp_amt, int_amt, fees_amt, late_fees):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        largest_line_id = None
        new_line_list = []
        if loan_id.installment_id:
            largest_line_id = max(loan_id.installment_id.ids)
        if largest_line_id:
            last_line_record = self.env['account.loan.installment'].browse(largest_line_id)
#             ins_num = int(last_line_record.name[-1])
            ins_num = self.get_last_installment_number(last_line_record.name)
            date_update = (datetime.datetime.strptime(last_line_record.date, '%Y-%m-%d').date())
            present_month = date_update.month
            new_day = int(date_update.day)
            for line in installments:
                if ins_num and date_update:
                    ins_num = ins_num + 1
                    present_month += 1
                    if present_month > 12:
                        present_month = present_month - 12;
                        s = date_update.year + 1
                        date_update = date_update.replace(year = s);
                    if new_day > 28:
                        date_update = line.loan_id.check_date(date_update, new_day, present_month)
                    date_update = date_update.replace(month = present_month);
                    new_line = self.create_new_installment(line, ins_num, date_update)
                    print(new_line,'new installment')
                    new_line_list.append(new_line)
#                     self._cr.execute("select payment_schedule_line_id from account_loan_installment_payment_schedule_line_rel \
#                         where account_loan_installment_id = %s"%line.id)
#                     installment_ids = self._cr.fetchall()
#                     if installment_ids:
#                         schedule_id = self.env['payment.schedule.line'].browse(installment_ids[0][0])
#                         schedule_id.capital -= line.outstanding_prin
#                         schedule_id.interest -= line.outstanding_int
#                         schedule_id.fees -= line.outstanding_fees
#                         schedule_id.total -= (line.outstanding_fees+line.outstanding_int+line.outstanding_prin)
#                         schedule_id.write({'installment_id':[(3, line.id)]})
#                         schedule_id.write({'date':new_line.date,'installment_id':[(4, new_line.id)]})
                    line.write({'outstanding_prin':0.0, 'outstanding_int':0.0,'due_principal': 0.0,'due_interest': 0.0,\
                                'due_fees': 0.0,'installment_due':0.0,'outstanding_fees':0.0,'late_fee':0.0,'capital':0.0,'interest':0.0,'fees':0.0,'total':0.0,'state':'skip'})
                   
            if cp_amt > 0.0 or int_amt > 0.0 or fees_amt > 0.0 or late_fees > 0.0:
                self.update_existed_line_with_extension(cp_amt, int_amt, fees_amt, late_fees)
                
            if new_line_list:
                if loan_id.payment_freq == 'quarterly':
                    self._get_calculation_quarterly()
                elif loan_id.payment_freq == 'half_yearly':
                    self._get_half_yearly()
                elif loan_id.payment_freq == 'monthly':
                    self._get_calculation_monthly()
                elif loan_id.payment_freq == 'yearly':
                    self._get_yearly()
    ##loan extension with no grace period ...................        
    def update_existed_installment(self, prin_total, int_amt, fee_amt, base_amt, tax_amt, late_fee_amount, late_base_amt, late_tax_amt, remove_ids, schedule_line_ids):
        remaining_line = self.env['account.loan.installment'].search([('id', 'not in', remove_ids),('loan_id','=',self._context.get('active_id'))])
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        if not remaining_line:
            raise Warning("You can not extends loan of selected period")
        add_prin_amt = 0.0
        add_int_amt = 0.0
        add_fee_amt = 0.0
        fee_base_amt = 0.0
        fee_tax_amt = 0.0
        fee_late_base_amt = 0.0
        fee_late_tax_amt = 0.0
        if remaining_line:
            if prin_total:
                add_prin_amt = round(prin_total / len(remaining_line), 2)
            if int_amt:
                add_int_amt = round(int_amt / len(remaining_line), 2)
            if fee_amt:
                add_fee_amt = round(fee_amt / len(remaining_line), 2)
            if base_amt:
                fee_base_amt = round(base_amt / len(remaining_line), 2)
            if tax_amt:
                fee_tax_amt = round(tax_amt / len(remaining_line), 2)
            
            if late_fee_amount:
                add_late_fee_amt = round(late_fee_amount / len(remaining_line), 2)
            if late_base_amt:
                fee_late_base_amt = round(late_base_amt / len(remaining_line), 2)
            if late_tax_amt:
                fee_late_tax_amt = round(late_tax_amt / len(remaining_line), 2)
                
        for rm_line in remaining_line:
            out_prin = add_prin_amt + rm_line.outstanding_prin
            out_int = add_int_amt + rm_line.outstanding_int
            out_fee = fee_base_amt + fee_tax_amt + rm_line.outstanding_fees
            cp_amt = add_prin_amt + rm_line.capital
            int_amt_tot = add_int_amt + rm_line.interest
            fees_amt_tot = fee_base_amt + fee_tax_amt + rm_line.fees
            total = (cp_amt + int_amt_tot + fees_amt_tot)
            out_late_fee = fee_late_base_amt + fee_late_tax_amt + rm_line.late_fee
            if out_fee > 0:
                for fee_line in rm_line.fee_lines:
                    base_tot = fee_line.base + fee_base_amt
                    tax_fee_tot = fee_line.tax + fee_tax_amt
                    fee_line.write({'base': base_tot, 'tax': tax_fee_tot})
            if out_late_fee > 0:
                search_ids = self.env['fees.lines'].search([('name', '=', 'late_fee'),('installment_id','=',rm_line.id)])
                if search_ids:
                    for fee_line in search_ids:
                        if fee_line.name == 'late_fee':
                            base_tot = fee_line.base + fee_late_base_amt
                            tax_fee_tot = fee_line.tax + fee_late_tax_amt
                            fee_line.write({'base': base_tot, 'tax': tax_fee_tot})
                else:
                    late_fee_product_id = False
                    for com_line in loan_id.loan_type.loan_component_ids:
                        if com_line.type == 'late_fee':
                            late_fee_product_id = com_line.product_id
                    if late_fee_product_id:
                        base_tot = fee_late_base_amt
                        tax_fee_tot = fee_late_tax_amt
                        fees_line_vals = {
                                'name':'late_fee',
                                'product_id':late_fee_product_id.id,
                                'base':base_tot,
                                'tax':tax_fee_tot,
                                'installment_id':rm_line.id
                                }
                        self.env['fees.lines'].create(fees_line_vals)
                
                
            rm_line.write({'outstanding_prin': out_prin, 'outstanding_int': out_int,\
                           'outstanding_fees': out_fee,'capital': cp_amt,'interest': int_amt_tot,'fees': fees_amt_tot,'late_fee':out_late_fee, 'total': total})
            
            ##affects on payment schedule lines .....................
            self._cr.execute("select payment_schedule_line_id from account_loan_installment_payment_schedule_line_rel \
                where account_loan_installment_id = %s"%rm_line.id)
            installment_ids = self._cr.fetchall()
            if installment_ids:
                schedule_id = self.env['payment.schedule.line'].browse(installment_ids[0][0])
                schedule_cp = add_prin_amt + schedule_id.capital
                schedule_int = add_int_amt + schedule_id.interest
                schedule_fees = fees_amt_tot + schedule_id.fees
                schedule_total =  (schedule_cp + schedule_int + schedule_fees)
                schedule_id.write({'capital':schedule_cp, 'interest':schedule_int,'fees':schedule_fees,'total':schedule_total})
                for id in schedule_line_ids:
                    schedule_id.write({'installment_id':[(4, id)]})
            print(rm_line.name) 
        paid_line = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id),('state', 'in', ['paid'])])
        for pl in paid_line:
            pl.due_principal = 0.0
            pl.due_interest = 0.0
            pl.due_fees = 0.0
            pl.installment_due = 0.0
        
            
    def extend_loan_by_grc(self, period_id, installment_id, grc):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        period = period_id.period
        count = 0
        prin_total = 0.0
        int_amt = 0.0
        fee_amt = 0.0
        base_amt = 0.0
        tax_amt = 0.0
        late_fee_amt = 0.0
        late_base_amt = 0.0
        late_tax_amt = 0.0
        remove_ids = []
        open_capital_amt = 0.0
        open_int_amt = 0.0
        open_fees_amt = 0.0
        open_late_fees = 0.0
        open_fee_base = 0.0
        open_fee_tx = 0.0
        open_late_base = 0.0
        open_late_tx = 0.0
        affected_lines = []
        schedule_affected_line = []
        flag = True
        inst_date = (datetime.datetime.strptime(installment_id.date, '%Y-%m-%d').date())
        for line in loan_id.installment_id:
            line_date = (datetime.datetime.strptime(line.date, '%Y-%m-%d').date())
            if line.state == 'open':
                line.capital = line.capital - line.outstanding_prin
                line.interest = line.interest - line.outstanding_int
                line.fees = line.fees - line.outstanding_fees
                line.total -= (line.outstanding_fees + line.outstanding_int + line.outstanding_prin)
                open_capital_amt += line.outstanding_prin
                open_int_amt += line.outstanding_int
                open_fees_amt += line.outstanding_fees
                open_late_fees += line.late_fee
                if grc == 'no_extension':
                    if line.late_fee:
                        for fee_line in line.fee_lines:
                            if fee_line.name == 'late_fee':
                                open_late_base = open_late_base + fee_line.base
                                open_late_tx = open_late_tx + fee_line.tax
                        for fee_line in line.fee_lines:
                            if fee_line.name == 'fees':
                                open_fee_base = open_fee_base + fee_line.base
                                open_fee_tx = open_fee_tx + fee_line.tax
                
                line.write({'state':'paid', 'outstanding_prin':0.0, 'outstanding_int':0.0, 'outstanding_fees':0.0, 'late_fee':0.0})
                
            if line_date >= inst_date and line.state not in ['paid', 'skip', 'open']:
#                 if line.outstanding_prin == 0 and line.outstanding_int == 0 and line.outstanding_fees == 0 and line.late_fee > 0:
#                     continue
                if grc == 'no_extension':
                    if line.outstanding_prin > 0:
                        prin_total = prin_total + line.outstanding_prin
                    if line.outstanding_int > 0:
                        int_amt = int_amt + line.outstanding_int
                    if line.outstanding_fees > 0:
                        fee_amt = fee_amt + line.outstanding_fees
                        for fee_line in line.fee_lines:
                            if fee_line.name == 'fees':
                                base_amt = base_amt + fee_line.base
                                tax_amt = tax_amt + fee_line.tax
                    if line.late_fee > 0:
                        late_fee_amt = late_fee_amt + line.outstanding_fees
                        for fee_line in line.fee_lines:
                            if fee_line.name == 'late_fee':
                                late_base_amt = late_base_amt + fee_line.base
                                late_tax_amt = late_tax_amt + fee_line.tax
                    ##affects on payment schedule lines .....................
                    self._cr.execute("select payment_schedule_line_id from account_loan_installment_payment_schedule_line_rel \
                        where account_loan_installment_id = %s"%line.id)
                    installment_ids = self._cr.fetchall()
                    if installment_ids:
                        schedule_affected_line.append(line.id)
                        schedule_id = self.env['payment.schedule.line'].browse(installment_ids[0][0])
                        schedule_cp = schedule_id.capital - line.capital
                        schedule_int = schedule_id.interest - line.interest
                        schedule_fees = schedule_id.fees - line.fees
                        schedule_total =  schedule_id.total - line.total
                        schedule_id.write({'capital':schedule_cp, 'interest':schedule_int,'fees':schedule_fees,'total':schedule_total})
                        schedule_id.write({'installment_id':[(3, line.id)]})
                        if schedule_id.capital == 0.0 and schedule_id.interest == 0.0 and \
                            schedule_id.fees == 0.0 and schedule_id.total == 0.0:
                            for inst_line in schedule_id.installment_id:
                                schedule_id.write({'installment_id':[(3, inst_line.id)]})
                            
                    line.write({'outstanding_prin':0.0, 'outstanding_int':0.0,'due_principal': 0.0,'due_interest': 0.0,\
                                'due_fees': 0.0,'installment_due':0.0,'outstanding_fees':0.0,'capital':0.0,'interest':0.0,'fees':0.0,'total':0.0,'late_fee':0.0,'state':'skip'})
                    
                elif grc == 'extension':
                    affected_lines.append(line)
                count += 1
            remove_ids.append(line.id)
            if count == period:
                flag = False
                break
            flag = True
        if flag:
            raise Warning("You can not extends loan of selected period")
        if grc == 'no_extension':
            prin_total += open_capital_amt
            int_amt += open_int_amt
            fee_amt += open_fees_amt
            base_amt += open_fee_base
            tax_amt += open_fee_tx
            late_fee_amt += open_late_fees
            late_base_amt += open_late_base
            late_tax_amt += open_late_tx
            self.update_existed_installment(prin_total, int_amt, fee_amt, base_amt, tax_amt, late_fee_amt,  late_base_amt, late_tax_amt, remove_ids, schedule_affected_line)
        elif grc == 'extension':
            self.add_existed_installment(affected_lines, open_capital_amt, open_int_amt, open_fees_amt, open_late_fees)
            
    #@api.multi
    def extend_period(self):
        if self.loan_extension:
            for loan in self._context['active_ids']:
                loan_id = self.env['account.loan'].browse(loan)
                if not loan_id.loan_type.interestversion_ids:
                    raise Warning("Please Check Loan Type.")
                mx_month = 0
                for tpe in loan_id.loan_type.interestversion_ids.interestversionline_ids:
                    if tpe.max_month:
                        mx_month = tpe.max_month
                if self.period_id and self.period_id.period > mx_month:
                    raise Warning("This loan can be extended beyond %s "%(mx_month) + "Months")
                if loan_id.loan_period:
#                     loan_id.loan_period = self.period_id.id
                    res = [i for i in loan_id.installment_id if i.state  not in ['open','paid','skip']] 
                    if res:
                        loan_id.total_installment = len(res) + self.period_id.period
    
                    wizard_id = self.env['loan.disbursement.wizard'].create({
                        'disbursement_amt': loan_id.loan_amount,
                        'name': 'Extended Period',
                        'date': self.installment_id.date,
                    })
                    wizard_id.with_context({'is_extended': True, 'active_id': loan_id.id, 'date': self.installment_id.date}).approve_loan()
        elif self.gp_with_no_extension and self.installment_id:
            self.extend_loan_by_grc(self.grc_period, self.installment_id, grc='no_extension')
        elif self.gp_with_extension and self.installment_id:
            self.extend_loan_by_grc(self.grc_period, self.installment_id, grc='extension')
        else:
            raise Warning("Please Select Loan Extension Method")
        return True
    
    def get_large_schedule_installment(self):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        largest_line_id = None
        ins_num = 0
        if loan_id.payment_schedule_ids:
            largest_line_id = max(loan_id.payment_schedule_ids.ids)
        if largest_line_id:
            last_line_record = self.env['payment.schedule.line'].browse(largest_line_id)
            ins_num = self.get_last_installment_number(last_line_record.name)
        return ins_num
    
    ##Quarterly calculation .................
    def _get_calculation_quarterly(self):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
#         large_cnt = self.get_large_schedule_installment()
        cnt = 0
        inst = 'installment'
        cnt1 = 1
#         cnt1 += 1
        cheque = 'cheque'
        principal = 0.0
        interest = 0.0
        fees = 0.0
        vals = {}
        installment_ids = []
        inst_list = []
        grc_installment = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id), ('state', 'not in', ['skip'])])
        if (len(grc_installment) % 3) != 0:
            raise UserError(_('You can not apply for quarterly basis loan. Please check no. of installments.'))
        if loan_id.payment_schedule_ids:
            loan_id.payment_schedule_ids.unlink()
        for line in grc_installment:
            principal = principal + line.capital
            interest = interest + line.interest
            fees = fees + line.fees
            installment_ids.append(line)
            inst_list.append(line.id)
            if cnt == 2:
                date_update = line.date  
                total =  principal + interest + fees
                vals.update({'name':inst+ str(cnt1), 'capital':principal,\
                             'interest':interest,'fees':fees,'total':total,\
                            'date':date_update, 'installment_id':[(6,0,inst_list)]})
                inst_list = []
                if loan_id.return_type == 'cheque':
                    vals1 = {'name':'cheque' + str(cnt1),\
                     'date':date_update, 'loan_id':loan_id.id,\
                     'code':'cheque' + str(cnt1),'partner_id':line.partner_id.id,\
                     'cheque_amount':total, 'loan':principal, 'interest':interest,\
                     'account_id':loan_id.journal_repayment_id.default_debit_account_id.id,\
                     'installment_id':line.id,'fees':fees}
                    cheque_id = self.env['account.loan.bank.cheque'].create(vals1)
                    vals.update({'cheque_id':cheque_id.id})
                    line.write({'cheque_id':cheque_id.id})
                    for l in installment_ids:
                        l.write({'cheque_id':cheque_id.id})
                    installment_ids = []
                        
                vals.update({'loan_id':loan_id.id})
                self.env['payment.schedule.line'].create(vals)
                vals = {}
                vals1 = {}
                principal = 0.0
                interest = 0.0
                fees = 0.0
                cnt1 = cnt1 + 1
                cnt = 0
            else:
                cnt = cnt + 1
                
    ## half yearly calculation ...........................
    def _get_half_yearly(self):
        cnt = 0
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        inst = 'installment'
        cnt1 = 1
        cheque = 'cheque'
        principal = 0.0
        interest = 0.0
        fees = 0.0
        installment_ids = []
        vals = {}
        inst_list = []
        if loan_id.payment_schedule_ids:
            loan_id.payment_schedule_ids.unlink()
        grc_installment = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id), ('state', 'not in', ['skip'])])
        if (len(grc_installment) % 6) != 0:
            raise UserError(_('You can not apply for half yearly loan. Please check no. of installments.'))
            
        for line in grc_installment:
            principal = principal + line.capital
            interest = interest + line.interest
            fees = fees + line.fees
            installment_ids.append(line)
            inst_list.append(line.id)
            if cnt == 5:
                date_update = line.date  
                total =  principal + interest + fees
                vals.update({'name':inst+ str(cnt1), 'capital':principal,\
                             'interest':interest,'fees':fees,'total':total,\
                            'date':date_update, 'installment_id':[(6,0,inst_list)]})
                inst_list = []
                if loan_id.return_type == 'cheque':
                    vals1 = {'name':'cheque' + str(cnt1),\
                     'date':date_update, 'loan_id':loan_id.id,\
                     'code':'cheque' + str(cnt1),'partner_id':line.partner_id.id,\
                     'cheque_amount':total, 'loan':principal, 'interest':interest,\
                     'account_id':loan_id.journal_repayment_id.default_debit_account_id.id,\
                     'installment_id':line.id, 'fees':fees}
                    cheque_id = self.env['account.loan.bank.cheque'].create(vals1)
                    vals.update({'cheque_id':cheque_id.id})
                    line.write({'cheque_id':cheque_id.id})
                    for l in installment_ids:
                        l.write({'cheque_id':cheque_id.id})
                    installment_ids = []
                vals.update({'loan_id':loan_id.id})
                self.env['payment.schedule.line'].create(vals)
                vals = {}
                vals1 = {}
                principal = 0.0
                interest = 0.0
                fees = 0.0
                cnt1 = cnt1 + 1
                cnt = 0
            else:
                cnt = cnt + 1
                
    ##monthly calculation .........................
    def _get_calculation_monthly(self):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        cnt1 = 1
        vals = {}
        inst = 'installment'
        cheque_cr = self.env['account.loan.bank.cheque']
        if loan_id.payment_schedule_ids:
            loan_id.payment_schedule_ids.unlink()
        grc_installment = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id), ('state', 'not in', ['skip'])])
        for line in grc_installment:
            vals = {'name':inst+ str(cnt1), 'capital':line.capital,\
                             'interest':line.interest,'fees':line.fees,'total':line.total,\
                            'date':line.date, 'installment_id':[(6,0,[line.id])],'loan_id':loan_id.id}
            if loan_id.return_type == 'cheque': 
                cheque_id = cheque_cr.create({'name':'cheque' + str(cnt1), 'date':line.date,\
                                        'loan_id':line.loan_id.id, 'code':'cheque' + str(cnt1),\
                                        'partner_id':line.partner_id.id,\
                                        'cheque_amount':line.total, 'loan':line.capital, 'interest':line.interest,\
                                        'account_id':loan_id.journal_repayment_id.default_debit_account_id.id,\
                                        'installment_id':line.id,'fees':line.fees})
                if cheque_id:
                    vals.update({'cheque_id':cheque_id.id})
                    line.write({'cheque_id':cheque_id.id})
#                     vals.update({'name':line.name, 'capital':line.capital,\
#                                      'interest':line.interest,'fees':line.fees,'total':line.total,\
#                                     'date':line.date, 'installment_id':line.id,'loan_id':self.id})
                    
            pyt_id = self.env['payment.schedule.line'].create(vals)
            cnt1 = cnt1 + 1
            
    ## yearly calcultion ..................
    def _get_yearly(self):
        loan_id = self.env['account.loan'].browse(self._context.get('active_id'))
        cnt = 0
        inst = 'installment'
        cnt1 = 1
        cheque = 'cheque'
        principal = 0.0
        interest = 0.0
        fees = 0.0
        installment_ids = []
        vals = {}
        inst_list = []
        grc_installment = self.env['account.loan.installment'].search([('loan_id', '=', loan_id.id), ('state', 'not in', ['skip'])])
        if (len(grc_installment) % 12) != 0:
            raise UserError(_('You can not apply for yearly basis loan. Please check no. of installments.'))
        if loan_id.payment_schedule_ids:
            loan_id.payment_schedule_ids.unlink()
            
        for line in grc_installment:
            principal = round(principal + line.capital,2)
            interest = round(interest + line.interest,2)
            fees = round(fees + line.fees,2)
            installment_ids.append(line)
            inst_list.append(line.id)
            if cnt == 11:
                date_update = line.date  
                total =  round(principal + interest + fees,2)
                vals.update({'name':inst+ str(cnt1), 'capital':principal,\
                             'interest':interest,'fees':fees,'total':total,\
                            'date':date_update, 'installment_id':[(6,0,inst_list)],'loan_id':loan_id.id})
                inst_list = []
                if loan_id.return_type == 'cheque':
                    vals1 = {'name':'cheque' + str(cnt1),\
                     'date':date_update, 'loan_id':loan_id.id,\
                     'code':'cheque' + str(cnt1),'partner_id':line.partner_id.id,\
                     'cheque_amount':total, 'loan':principal, 'interest':interest,\
                     'account_id':loan_id.journal_repayment_id.default_debit_account_id.id,\
                     'installment_id':line.id,'fees':fees}
                    cheque_id = self.env['account.loan.bank.cheque'].create(vals1)
                    vals.update({'cheque_id':cheque_id.id})
                    line.write({'cheque_id':cheque_id.id})
                    for l in installment_ids:
                        l.write({'cheque_id':cheque_id.id})
                    installment_ids = []
#                 vals.update({'loan_id':self.id})
                self.env['payment.schedule.line'].create(vals)
                vals = {}
                vals1 = {}
                principal = 0.0
                interest = 0.0
                fees = 0.0
                cnt1 = cnt1 + 1
                cnt = 0
            else:
                cnt = cnt + 1