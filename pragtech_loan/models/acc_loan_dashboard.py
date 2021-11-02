from odoo import models, api, fields, _,SUPERUSER_ID
import json
from datetime import datetime,date,timedelta
import datetime as dt
# import operator
from odoo.tools.misc import formatLang
from dateutil.relativedelta import *



out_graph_flag = False
out_graph_data = []
total_outstanding_amt = 0.0
currency = None
realization_graph_flag = False
realization_graph_data = []
rel_currency = None
final_total_principle = 0.00
final_total_interest = 0.00
final_total_fees = 0.00



class account_loan_dashboard(models.Model):
    _name = 'account.loan.dashboard'


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(account_loan_dashboard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        global realization_graph_flag
        realization_graph_flag = False
        global out_graph_flag
        out_graph_flag = False
        global out_graph_data
        out_graph_data = []
        global total_outstanding_amt
        total_outstanding_amt = 0.0
        global currency
        currency = None
        global realization_graph_data
        realization_graph_data = []
        global rel_currency
        rel_currency = None
        global final_total_principle
        final_total_principle = 0.00
        global final_total_interest
        final_total_interest = 0.00
        global final_total_fees
        final_total_fees = 0.00
        return res

    #@api.one
    def _get_count(self):
        '''
            Compute method used to get data for multiple fields
        '''
#         loan_obj = self.env['account.loan']
        if not (self._uid == SUPERUSER_ID ):
            self._cr.execute('select count(id) from account_loan where company_id={}'.format(self.env.user.company_id.id))
            loan_count1 = self._cr.fetchone()
            if loan_count1:
                loan_count = loan_count1[0]
            else:
                loan_count = 0
#             loan_count = loan_obj.sudo().search([('company_id','=',self.env.user.company_id.id)])
            self._cr.execute("select count(id) from account_loan where company_id={} and state='draft'".format(self.env.user.company_id.id))
            new_loan1 = self._cr.fetchone()
            if new_loan1:
                new_loan = new_loan1[0]
            else:
                new_loan = 0
#             new_loan = loan_obj.sudo().search([('state', '=', 'draft'),('company_id','=',self.env.user.company_id.id)])
            self._cr.execute("select count(id) from account_loan where company_id={} and state='done'".format(self.env.user.company_id.id))
            loan_done_count1 = self._cr.fetchone()
            if loan_done_count1:
                loan_done_count = loan_done_count1[0]
            else:
                loan_done_count = loan_done_count1[0]

#             loan_done_count = loan_obj.sudo().search([('state', '=', 'done'),('company_id','=',self.env.user.company_id.id)])
            self._cr.execute("select count(id) from account_loan where company_id={} and state='apply'".format(self.env.user.company_id.id))
            loan_sanctioned_count1 = self._cr.fetchone()
            if loan_sanctioned_count1:
                loan_sanctioned_count = loan_sanctioned_count1[0]
            else:
                loan_sanctioned_count = loan_sanctioned_count1[0]
#             loan_sanctioned_count = loan_obj.sudo().search([('state', '=', 'apply'),('company_id','=',self.env.user.company_id.id)])
            self._cr.execute("select count(id) from account_loan where company_id={} and state='approved'".format(self.env.user.company_id.id))
            loan_disbursed_count1 = self._cr.fetchone()
            if loan_disbursed_count1:
                loan_disbursed_count = loan_disbursed_count1[0]
            else:
                loan_disbursed_count = loan_disbursed_count1[0]
#             loan_disbursed_count = loan_obj.sudo().search([('state', '=', 'approved'),('company_id','=',self.env.user.company_id.id)])
            self._cr.execute("select count(id) from account_loan where company_id={} and state='partial'".format(self.env.user.company_id.id))
            loan_partial_count1 = self._cr.fetchone()
            if loan_partial_count1:
                loan_partial_count = loan_partial_count1[0]
            else:
                loan_partial_count = loan_partial_count1[0]
#             loan_partial_count = loan_obj.sudo().search([('state', '=', 'partial'),('company_id','=',self.env.user.company_id.id)])
            self._cr.execute("select count(id) from account_loan where company_id={} and state='cancel'".format(self.env.user.company_id.id))
            loan_cancel_count1 = self._cr.fetchone()
            if loan_cancel_count1:
                loan_cancel_count = loan_cancel_count1[0]
            else:
                loan_cancel_count = loan_cancel_count1[0]
#             loan_cancel_count = loan_obj.sudo().search([('state', '=', 'cancel'),('company_id','=',self.env.user.company_id.id)])
        else:
            self._cr.execute('select count(id) from account_loan')
            loan_count1 = self._cr.fetchone()
            if loan_count1:
                loan_count = loan_count1[0]
            else:
                loan_count = 0
#             loan_count = loan_obj.sudo().search([])\
            self._cr.execute("select count(id) from account_loan where state='draft'")
            new_loan1 = self._cr.fetchone()
            if new_loan1:
                new_loan = new_loan1[0]
            else:
                new_loan = 0
#             new_loan = loan_obj.sudo().search([('state', '=', 'draft')])
            self._cr.execute("select count(id) from account_loan where state='done'")
            loan_done_count1 = self._cr.fetchone()
            if loan_done_count1:
                loan_done_count = loan_done_count1[0]
            else:
                loan_done_count = loan_done_count1[0]
#             loan_done_count = loan_obj.sudo().search([('state', '=', 'done')])
            self._cr.execute("select count(id) from account_loan where state='apply'")
            loan_sanctioned_count1 = self._cr.fetchone()
            if loan_sanctioned_count1:
                loan_sanctioned_count = loan_sanctioned_count1[0]
            else:
                loan_sanctioned_count = loan_sanctioned_count1[0]
#             loan_sanctioned_count = loan_obj.sudo().search([('state', '=', 'apply')])
            self._cr.execute("select count(id) from account_loan where state='approved'")
            loan_disbursed_count1 = self._cr.fetchone()
            if loan_disbursed_count1:
                loan_disbursed_count = loan_disbursed_count1[0]
            else:
                loan_disbursed_count = loan_disbursed_count1[0]
#             loan_disbursed_count = loan_obj.sudo().search([('state', '=', 'approved')])
            self._cr.execute("select count(id) from account_loan where state='partial'")
            loan_partial_count1 = self._cr.fetchone()
            if loan_partial_count1:
                loan_partial_count = loan_partial_count1[0]
            else:
                loan_partial_count = loan_partial_count1[0]
#             loan_partial_count = loan_obj.sudo().search([('state', '=', 'partial')])
            self._cr.execute("select count(id) from account_loan where state='cancel'")
            loan_cancel_count1 = self._cr.fetchone()
            if loan_cancel_count1:
                loan_cancel_count = loan_cancel_count1[0]
            else:
                loan_cancel_count = loan_cancel_count1[0]
#             loan_cancel_count = loan_obj.sudo().search([('state', '=', 'cancel')])

        self.loan_count = loan_count
        self.loan_done_count = loan_done_count
        self.loan_sanctioned_count = loan_sanctioned_count
        self.loan_disbursed_count = loan_disbursed_count
        self.loan_partial_count = loan_partial_count
        self.loan_cancel_count = loan_cancel_count
        self.new_loan = new_loan

    #@api.one
    def _get_total_amount(self):
        current_date = datetime.now()
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done']),('company_id','=',self.env.user.company_id.id)])
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done'])])
        total = 0.00
        cur_id = None

        for loan in loan_obj:
            cur_id = None
            if loan.journal_disburse_id:
                if loan.journal_disburse_id.currency_id:
                    cur_id = loan.journal_disburse_id.currency_id
                else:
                    cur_id = loan.journal_disburse_id.company_id.currency_id
            if loan.disbursement_details:
                for dis in loan.disbursement_details:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            l1 = line.credit
#                             if loan.company_id.currency_id and loan.company_id.currency_id.id != line.journal_id.currency_id.id:
#                                 total += loan.company_id.currency_id.with_context(date=current_date).compute(l1, line.journal_id.currency_id)
#                             else:
                            total += l1


#                 l1 = [line.credit for dis in loan.disbursement_details if dis.release_number.state == 'posted' for line in dis.release_number.line_ids]
#                 total += sum(l1)
        if cur_id:
#             if total > 1000000:
#                 tot_in_million = round(total / 1000000, 4)
#                 total = tot_in_million
#                 self.total_amt = str(total) + ' Millions'
#             else:
            self.total_amt = formatLang(self.env, cur_id.round(total) + 0.0, currency_obj=cur_id)
        else:
            self.total_amt = 0.00

    #@api.one
    def _kanban_dashboard_graph(self):
        self.kanban_dashboard_graph = json.dumps(self.get_bar_graph_datas())

    #@api.one
    def _sector_graph(self):
        self.sector_graph = json.dumps(self.get_sector_datas())

    #@api.one
    def _delinquency_graph(self):
        self.delinquency_graph = json.dumps(self.get_delinquency_datas())

    #@api.one
    def _par_graph(self):
        self.par_graph = json.dumps(self.get_par_datas())

    #@api.one
    def _gender_graph(self):
        self.gender_graph = json.dumps(self.get_gender_datas())

    #@api.one
    def _out_graph(self):
        self.outstanding_graph = json.dumps(self.get_out_datas())

    #@api.one
    def _realization_graph(self):
        self.realization_graph = json.dumps(self.get_realization_datas())

    #@api.one
    def _get_loan_decline_amt(self):
        cur_id = None
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['cancel']),('company_id','=',self.env.user.company_id.id)])
            cur_id = self.env.user.company_id.currency_id
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['cancel'])])
            cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        total = 0.00
        for loan in loan_obj:
#             cur_id = None
#             if loan.journal_disburse_id:
#                 if loan.journal_disburse_id.currency_id:
#                     cur_id = loan.journal_disburse_id.currency_id
#                 else:
#                     cur_id = loan.journal_disburse_id.company_id.currency_id
            if loan.disbursement_details:
                for dis in loan.disbursement_details:
#                     if dis.release_number.state == 'posted':
#                         for line in dis.release_number.line_ids:
#                             l1 = line.credit
                    total += dis.disbursement_amt
#         cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        if cur_id:
            self.loan_cancel_total = formatLang(self.env, cur_id.round(total) + 0.0, currency_obj=cur_id)
        else:
            self.loan_cancel_total = 0.00

    #@api.one
    def _get_loan_partially_amt(self):
        cur_id = None
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial']),('company_id','=',self.env.user.company_id.id)])
            cur_id = self.env.user.company_id.currency_id
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial'])])
            cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        total = 0.00
#         cur_id = None
        for loan in loan_obj:
#             cur_id = None
#             if loan.journal_disburse_id:
#                 if loan.journal_disburse_id.currency_id:
#                     cur_id = loan.journal_disburse_id.currency_id
#                 else:
#                     cur_id = loan.journal_disburse_id.company_id.currency_id
            if loan.disbursement_details:
                for dis in loan.disbursement_details:
#                     if dis.release_number.state == 'posted':
#                         for line in dis.release_number.line_ids:
#                             l1 = line.credit
                    total += dis.disbursement_amt
#         cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        if cur_id:
            self.loan_partial_total = formatLang(self.env, cur_id.round(total) + 0.0, currency_obj=cur_id)
        else:
            self.loan_partial_total = 0.00


    #@api.one
    def _get_loan_done_amt(self):
        cur_id = None
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['done']),('company_id','=',self.env.user.company_id.id)])
            cur_id = self.env.user.company_id.currency_id
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['done'])])
            cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        total = 0.00
#         cur_id = None
        for loan in loan_obj:
#             cur_id = None
#             if loan.journal_disburse_id:
#                 if loan.journal_disburse_id.currency_id:
#                     cur_id = loan.journal_disburse_id.currency_id
#                 else:
#                     cur_id = loan.journal_disburse_id.company_id.currency_id
            if loan.disbursement_details:
                for dis in loan.disbursement_details:
#                     if dis.release_number.state == 'posted':
#                         for line in dis.release_number.line_ids:
#                             l1 = line.credit
                    total += dis.disbursement_amt
#         cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        if cur_id:
            self.loan_done_total = formatLang(self.env, cur_id.round(total) + 0.0, currency_obj=cur_id)
        else:
            self.loan_done_total = 0.00


    #@api.one
    def _get_loan_disbursed_amt(self):
        cur_id = None
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['approved']),('company_id','=',self.env.user.company_id.id)])
            cur_id = self.env.user.company_id.currency_id
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['approved'])])
            cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        total = 0.00
#         cur_id = None
        for loan in loan_obj:
#             cur_id = None
#             if loan.journal_disburse_id:
#                 if loan.journal_disburse_id.currency_id:
#                     cur_id = loan.journal_disburse_id.currency_id
#                 else:
#                     cur_id = loan.journal_disburse_id.company_id.currency_id
            if loan.disbursement_details:
                for dis in loan.disbursement_details:
#                     if dis.release_number.state == 'posted':
#                         for line in dis.release_number.line_ids:
#                             l1 = line.credit
                    total += dis.disbursement_amt
#         cur_id = self.env['res.currency'].search([('name', '=', 'RWF'),('symbol', '=', 'RWF')], limit=1)
        if cur_id:
            self.loan_disbursed_total = formatLang(self.env, cur_id.round(total) + 0.0, currency_obj=cur_id)
        else:
            self.loan_disbursed_total = 0.00

    sector_graph = fields.Text(compute='_sector_graph')
    delinquency_graph = fields.Text(compute='_delinquency_graph')
    par_graph = fields.Text(compute='_par_graph')
    outstanding_graph = fields.Text(compute='_out_graph')
    realization_graph = fields.Text(compute='_realization_graph')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    loan_count = fields.Integer(compute='_get_count')
    loan_done_count = fields.Integer(compute='_get_count')
    loan_sanctioned_count = fields.Integer(compute='_get_count')
    loan_disbursed_count = fields.Integer(compute='_get_count')
    loan_partial_count = fields.Integer(compute='_get_count')
    loan_cancel_count = fields.Integer(compute='_get_count')
    new_loan = fields.Integer(compute='_get_count')
    delinquency_percent = fields.Char()
    par_percent = fields.Char()
    is_group = fields.Boolean()
#     company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    total_amt = fields.Char(compute='_get_total_amount')
    total_out_amt = fields.Char()
    total_principle = fields.Char()
    total_interest = fields.Char()
    total_fees = fields.Char()
    gender_graph = fields.Text(compute='_gender_graph')
    gender_percent = fields.Float(compute='_get_gender_percent')
    loan_disbursed_total = fields.Char(compute='_get_loan_disbursed_amt')
    loan_done_total = fields.Char(compute='_get_loan_done_amt')
    loan_partial_total = fields.Char(compute='_get_loan_partially_amt')
    loan_cancel_total = fields.Char(compute='_get_loan_decline_amt')

    def _graph_title_and_key(self):
        return ['', _('Loan: Disbursed Amount')]

    #@api.multi
    def get_bar_graph_datas(self):
        '''
            Called from Compute method to calculate data for Loan Disbursement Details tab
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        past_total = 0.00
        present = 0.00
        ps1 = 0.00
        ps2 = 0.00
        ps3 = 0.00
#         if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
#             loan_obj = self.env['account.loan'].sudo().search([('company_id','=',self.env.user.company_id.id)])
#         else:
#             loan_obj = self.env['account.loan'].sudo().search([])
#
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done']),('company_id','=',self.env.user.company_id.id)])
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done'])])
        dt = datetime.today()
        for loan in loan_obj:
            for dis in loan.disbursement_details:
                if str(dt.year) in dis.bill_date:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            present += line.credit
                elif str(dt.year - 1) in dis.bill_date:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            ps1 += line.credit
                elif str(dt.year - 2) in dis.bill_date:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            ps2 += line.credit
                elif str(dt.year - 3) in dis.bill_date:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            ps3 += line.credit
                else:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            past_total += line.credit

        data = [{'value': past_total, 'label': 'Past'},
                {'value': ps3, 'label': str(dt.year - 3)},
                {'value': ps2, 'label': str(dt.year - 2)},
                {'value': ps1, 'label': str(dt.year - 1)},
                {'value': present, 'label': 'This Year'}]

        [graph_title, graph_key] = self._graph_title_and_key()
        return [{'values': data, 'title': graph_title, 'key': graph_key}]

    #@api.multi
    def get_realization_datas(self):
        '''
            This method is called from compute method to calculate data for Realization Graph data
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        global realization_graph_flag
        if realization_graph_flag == False:
            global final_total_principle, final_total_interest, final_total_fees, realization_graph_data, rel_currency
            realization_graph_flag = True
            total_principle = 0.00
            total_interest = 0.00
            total_fees = 0.00
            current_date = datetime.now()
            last_currency = None
            start_date = datetime.strptime(str(date.today()), "%Y-%m-%d").date()
            end_date = date.today() + relativedelta(months=1)
#             relativedelta(months=+int(self.pro_month))
#             end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
            if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
                loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved']), ('company_id','=',self.env.user.company_id.id)])
            else:
                loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved'])])
            cur_id = None
            prin_am_tot = 0.0
            for loan in loan_obj:
                local_total_principle = 0.0
                local_total_interest = 0.0
                local_total_fees = 0.0
                cur_id = None
                if loan.journal_disburse_id:
                    if loan.journal_disburse_id.currency_id:
                        cur_id = loan.journal_disburse_id.currency_id
                    else:
                        cur_id = loan.journal_disburse_id.company_id.currency_id
                local_exp_pri = local_exp_int = local_exp_fees = 0
#                 self._cr.execute("select id, outstanding_prin, outstanding_int, outstanding_fees from account_loan_installment where date >= '{}' and date <= '{}' and loan_id = '{}'".format(start_date, end_date, loan.id))
#                 installment_ids = self._cr.fetchall()

                self._cr.execute("select id from payment_schedule_line where date >= '{}' and date <= '{}' and loan_id = '{}'".format(start_date, end_date, loan.id))
                schedule_ids = self._cr.fetchall()
                installments = [[0,0,0]]
                installment_ids = []
                if schedule_ids:
                    for o in schedule_ids:
                        self._cr.execute("select account_loan_installment_id from account_loan_installment_payment_schedule_line_rel \
                        where payment_schedule_line_id = %s"%o[0])
                        installment_ids = self._cr.fetchall()
                        for i in installment_ids:
                            if i:
                                self._cr.execute("select sum(outstanding_prin), sum(outstanding_int), sum(outstanding_fees) from account_loan_installment where id = %s"%i[0])
                                installments = self._cr.fetchall()
                                if installments[0] is not None:
                                    local_total_principle += installments[0][0]
                                if installments[0] is not None:
                                    local_total_interest += installments[0][1]
                                if installments[0] is not None:
                                    if installments[0][2] is not None:
                                        local_total_fees += installments[0][2]
                #Covert all values if currency is different
                if cur_id and cur_id.id != loan.company_id.currency_id.id:
                    local_exp_pri = cur_id.with_context(date=current_date).compute(local_total_principle, loan.company_id.currency_id)
                    local_exp_int = cur_id.with_context(date=current_date).compute(local_total_interest, loan.company_id.currency_id)
                    local_exp_fees = cur_id.with_context(date=current_date).compute(local_total_fees, loan.company_id.currency_id)
                    total_principle += local_exp_pri
                    total_interest += local_exp_int
                    total_fees += local_exp_fees

                else:
                    total_principle += round(local_total_principle,2)
                    total_interest += round(local_total_interest,2)
                    total_fees += round(local_total_fees,2)

                last_currency = loan.company_id.currency_id
#             self._cr.execute("select sum(outstanding_prin),sum(outstanding_int),sum(outstanding_fees) from account_loan_installment where id in (select account_loan_installment_id from account_loan_installment_payment_schedule_line_rel where payment_schedule_line_id in (select id from payment_schedule_line where date >=%s and date <=%s and loan_id in (select id from account_loan where state in ('partial', 'approved'))))",(start_date, end_date))
#             aa = self._cr.fetchone()
#             print (aa,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

            #Set Global Variable Values
            final_total_principle = total_principle
            final_total_interest = total_interest
            final_total_fees = total_fees
            #Set Fields
            self.total_principle = formatLang(self.env, round(total_principle,2))
            self.total_interest = round(total_interest,2)
            self.total_fees = round(total_fees, 2)
            rel_currency = last_currency
            #Create Graph data List
            data = [{'value': total_principle, 'label': 'Principle'},
                    {'value': total_interest, 'label': 'Interest'},
                    {'value': total_fees, 'label': 'Fees'},]
            realization_graph_data = [{'values': data, 'title': '', 'key': _('Realization')}]
            return realization_graph_data
        else:
            if rel_currency:
                self.total_principle = formatLang(self.env, rel_currency.round(final_total_principle) + 0.0, currency_obj=rel_currency)
                self.total_interest = formatLang(self.env, rel_currency.round(final_total_interest) + 0.0, currency_obj=rel_currency)
                self.total_fees = formatLang(self.env, rel_currency.round(final_total_fees) + 0.0, currency_obj=rel_currency)
            else:
                self.total_principle = final_total_principle
                self.total_interest = final_total_interest
                self.total_fees = final_total_fees
            return realization_graph_data

    #@api.multi
    def get_out_datas(self):
        '''
            Called from Compute method to calculate data for outstanding tab
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        global out_graph_flag
        if out_graph_flag == False:
            out_graph_flag = True
            date_new = datetime.now()
            today = str(date.today())
            pri = 0.00
            intr = 0.00
            fees = 0.00
            late_fees = 0.00
            due_prin = 0.0
            par30 = 0.0
            bal_pri = 0.0
            bal_int = 0.0
            bal_fees = 0.0
            current_date = datetime.strptime(today, "%Y-%m-%d")
            previous_date = current_date + timedelta(-30)
            if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
                loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done']),('approve_date','<=',datetime.strptime(today, "%Y-%m-%d")),('company_id','=',self.env.user.company_id.id)])
            else:
                loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done']),('approve_date','<=',datetime.strptime(today, "%Y-%m-%d"))])
            cur_id = None
            for loan in loan_obj:
                cur_id = None
                tot_bal_pri = 0.0
                tot_bal_int = 0.0
                tot_bal_fees = 0.0
                tot_bal_late_fees = 0.0
                paid_capital = 0.0
                paid_interest = 0.0
                paid_fee = 0.0
                paid_late_fee = 0.0
                bal_due_prin = 0.0
                bal_lst_30_prin = 0.0
                bal_pri1 = 0.0
                bal_pri30day = 0.0
                tot_prin = 0.0
                tot_prin_30day = 0.0
                arrear_day = 0
#                 tot_ff = 0.0

                if loan.journal_disburse_id:
                    if loan.journal_disburse_id.currency_id:
                        cur_id = loan.journal_disburse_id.currency_id
                    else:
                        cur_id = loan.journal_disburse_id.company_id.currency_id

                if loan.journal_disburse_id:
                    if loan.journal_disburse_id.currency_id:
                        cur_id = loan.journal_disburse_id.currency_id
                    else:
                        cur_id = loan.journal_disburse_id.company_id.currency_id

                for pay in loan.payment_schedule_ids:
                    final_date = pay.date
                    pay_flag = 0
                    for pay_ins in pay.installment_id:
                        if datetime.strptime(pay.date, "%Y-%m-%d") <= current_date and pay_ins.state != 'paid':
                            if not arrear_day:
                                arrear_day = pay.date
                                break
                if arrear_day:
                        arrear_day = datetime.strptime(arrear_day, "%Y-%m-%d")
                        arrear_day = date_new - arrear_day
                        arrear_day = arrear_day.days

                for inst in loan.installment_id:
                    tot_bal_pri += inst.capital
                    tot_bal_int += inst.interest
                    tot_bal_fees += inst.fees
                    tot_bal_late_fees += inst.late_fee

#                     date_inst = datetime.strptime(inst.date, "%Y-%m-%d")
                    self._cr.execute("select prin_amt, int_amt, fees_amt, late_fee_amt from payment_details where pay_date <= '{}' and line_id = {} and state != '{}'".format(current_date, inst.id, 'cancel'))
                    paid_line_ids = self._cr.fetchall()
                    for paid_line in paid_line_ids:
                        if paid_line[0] is not None:
                            paid_capital += paid_line[0]
                        if paid_line[1] is not None:
                            paid_interest += paid_line[1]
                        if paid_line[2] is not None:
                            paid_fee += paid_line[2]
                        if paid_line[3] is not None:
                            paid_late_fee += paid_line[3]

                    schedule_line_ids = self.env['payment.schedule.line'].search([('date','<=',datetime.strptime(today, "%Y-%m-%d")),('installment_id','in', [inst.id])])
                    if schedule_line_ids:
                        l1 = [l.capital for l in schedule_line_ids.installment_id if inst.id == l.id]
                        tot_prin += sum(l1)
                        if arrear_day > 30:
                            tot_prin_30day += sum(l1)
#                         ld1 = [l.capital for l in schedule_line_ids.installment_id if inst.id == l.id and (datetime.strptime(l.date, "%Y-%m-%d") >= previous_date and datetime.strptime(l.date, "%Y-%m-%d") <= current_date)]
#                         tot_prin_30day += sum(ld1)
#                         for l in schedule_line_ids.installment_id:
#                             if l.id == inst.id and (datetime.strptime(l.date, "%Y-%m-%d") >= previous_date and datetime.strptime(l.date, "%Y-%m-%d") <= current_date):
#                                 pay_line30day = self.env['payment.details'].search([('line_id','=',l.id),('state','!=','cancel')])
#                                 l2_30day = [pline.prin_amt for pline in pay_line30day if pline.pay_date if datetime.strptime(pline.pay_date, "%Y-%m-%d").date() <= datetime.strptime(today, "%Y-%m-%d").date()]
#                                 bal_pri30day += sum(l2_30day)
                    ##exactly calculated by installment linesssssssssssssss..............
#                     if inst.date and datetime.strptime(inst.date, "%Y-%m-%d") >= previous_date and datetime.strptime(inst.date, "%Y-%m-%d") <= current_date:
#                         tot_prin_30day += inst.capital
#                         self._cr.execute("select prin_amt from payment_details where pay_date >= '{}' and pay_date <= '{}'and line_id = {} and state != '{}'".format(previous_date, current_date, inst.id, 'cancel'))
#                         paid_lines = self._cr.fetchall()
#                         for paid_line in paid_lines:
#                             if paid_line[0] is not None:
#                                 bal_pri30day += paid_line[0]

                    if inst.date and datetime.strptime(inst.date, "%Y-%m-%d").date() <= datetime.strptime(today, "%Y-%m-%d").date():
                        pay_line = self.env['payment.details'].search([('line_id','=',inst.id),('state','!=','cancel')])
                        if pay_line:
                            l2 = [pline.prin_amt for pline in pay_line if pline.pay_date if datetime.strptime(pline.pay_date, "%Y-%m-%d").date() <= datetime.strptime(today, "%Y-%m-%d").date()]
                            bal_pri1 += sum(l2)
                            if arrear_day > 30:
                                bal_pri30day += sum(l2)
#                             ld2 = [pline.prin_amt for pline in pay_line if pline.pay_date if datetime.strptime(pline.pay_date, "%Y-%m-%d") >= previous_date and datetime.strptime(pline.pay_date, "%Y-%m-%d") <= current_date]
#                             bal_pri30day += sum(l2)
                    ##30days calculation .................
#                     print(datetime.strptime(inst.date, "%Y-%m-%d"),type(datetime.strptime(inst.date, "%Y-%m-%d"), previous_date, type(previous_date), current_date, type(current_date)), 'fffffffffffffffffffffffffffffffffffffff')
#                     if inst.date and datetime.strptime(inst.date, "%Y-%m-%d") >= previous_date and datetime.strptime(inst.date, "%Y-%m-%d") <= current_date:
#                         pay_line = self.env['payment.details'].search([('line_id','=',inst.id),('state','!=','cancel')])
#                         if pay_line:
#                             ld2 = [pline.prin_amt for pline in pay_line if pline.pay_date if datetime.strptime(pline.pay_date, "%Y-%m-%d") >= previous_date and datetime.strptime(pline.pay_date, "%Y-%m-%d") <= current_date]
#                             bal_pri30day += sum(ld2)

#                     if inst.date and  datetime.strptime(inst.date, "%Y-%m-%d") <= datetime.strptime(today, "%Y-%m-%d") and inst.state != 'paid':  # == 'draft'
#                                 '''Get Amount Past Due'''
#                                 schedule_line = self.env['payment.schedule.line'].search([('date','<=',datetime.strptime(today, "%Y-%m-%d")),('installment_id','in', [inst.id])])
# #                                 past_pri += inst.due_principal
# #                                 past_int += inst.due_interest
# #                                 past_fees += inst.due_fees
#                                 if schedule_line:
#                                     for l in schedule_line_ids.installment_id:
#                                         if inst.id == l.id:
#                                             bal_due_prin += l.due_principal
                #### for total outstanding amount ####
                int_to_bal = paid_interest
                paid_fee_to_bal = paid_fee
                paid_late_fee_bal = paid_late_fee

                current_date = datetime.strptime(today, "%Y-%m-%d")
                # self._cr.execute("select waived_off, is_carry_forward, amount from waived_entries where is_cancel = {} and loan_id = {} and date <= '{}'".format(False, loan.id, current_date))
                # waived_line_ids = self._cr.fetchall()
                # for waived_line in waived_line_ids:
                #     if (waived_line[0] is not None) and (waived_line[1] is not None):
                #         if waived_line[0] == 'Interest' and (not waived_line[1]):
                #             int_to_bal += waived_line[2]
                #         if waived_line[0] == 'Fees' and (not waived_line[1]):
                #             paid_fee_to_bal += waived_line[2]
                #         if waived_line[0] == 'Late Fees' and (not waived_line[1]):
                #             paid_late_fee_bal += waived_line[2]

                if tot_prin > bal_pri1:
                    bal_due_prin = round(tot_prin - bal_pri1,2)
                if tot_prin_30day > bal_pri30day:
                    bal_lst_30_prin = round(tot_prin_30day - bal_pri30day, 2)

                bal_pri = round(tot_bal_pri - paid_capital, 2)
                bal_int = round(tot_bal_int - int_to_bal, 2)
                bal_fees = round(tot_bal_fees - paid_fee_to_bal, 2)
                late_fee = round(tot_bal_late_fees - paid_late_fee_bal, 2)
                if cur_id and cur_id.id != loan.company_id.currency_id.id:
                    pri += cur_id.with_context(date=date_new).compute(bal_pri, loan.company_id.currency_id)
                    intr += cur_id.with_context(date=date_new).compute(bal_int, loan.company_id.currency_id)
                    fees += cur_id.with_context(date=date_new).compute(bal_fees, loan.company_id.currency_id)
                    late_fees += cur_id.with_context(date=date_new).compute(late_fee, loan.company_id.currency_id)
                    due_prin += cur_id.with_context(date=date_new).compute(bal_due_prin, loan.company_id.currency_id)
                    if bal_lst_30_prin:
                        par30 += cur_id.with_context(date=date_new).compute(bal_lst_30_prin, loan.company_id.currency_id)
                else:
                    pri += bal_pri
                    intr += bal_int
                    fees += bal_fees
                    late_fees += late_fee
                    due_prin += bal_due_prin
                    if bal_lst_30_prin:
                        par30 += bal_lst_30_prin
            global total_outstanding_amt, currency, out_graph_data
            total_outstanding_amt = pri + intr + fees + late_fees
            if cur_id:
                currency = cur_id
                self.total_out_amt = formatLang(self.env, cur_id.round(total_outstanding_amt) + 0.0, currency_obj=cur_id)
            else:
                self.total_out_amt = total_outstanding_amt
            data = [{'value': pri, 'label': 'Principle'},
                    {'value': intr, 'label': 'Interest'},
                    {'value': fees, 'label': 'Fees'},
                    {'value': late_fees, 'label': 'Late Fees'},
#                     {'value': due_prin, 'label': 'Due Prin'}
                    ]

            out_graph_data = [{'values': data, 'due_prin':due_prin, 'par_30':par30, 'title': '', 'key': _('Outstanding Amount')}]
            return out_graph_data
        else:
            if currency:
                self.total_out_amt = formatLang(self.env, currency.round(total_outstanding_amt) + 0.0, currency_obj=currency)
            else:
                self.total_out_amt = total_outstanding_amt
            return out_graph_data

#     #@api.multi
#     def get_out_datas(self):
#         '''
#             Called from Compute method to calculate data for outstanding tab
#             params : self
#             return : a list of dictionary that needs to be dumped into JSON format
#         '''
#         date_new = datetime.now()
#         pri = 0.00
#         intr = 0.00
#         fees = 0.00
#         late_fees = 0.00
#         if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
#             loan_obj = self.env['account.loan'].sudo().search([('company_id','=',self.env.user.company_id.id)])
#         else:
#             loan_obj = self.env['account.loan'].sudo().search([])
#         for loan in loan_obj:
#             cur_id = None
#             if loan.journal_disburse_id:
#                 if loan.journal_disburse_id.currency_id:
#                     cur_id = loan.journal_disburse_id.currency_id
#                 else:
#                     cur_id = loan.journal_disburse_id.company_id.currency_id
#             for ins in loan.installment_id:
#                 if cur_id:
#                     pri += cur_id.with_context(date=date_new).compute(ins.outstanding_prin, loan.company_id.currency_id)
#                     intr += cur_id.with_context(date=date_new).compute(ins.outstanding_int, loan.company_id.currency_id)
#                     fees += cur_id.with_context(date=date_new).compute(ins.outstanding_fees, loan.company_id.currency_id)
#                     late_fees += cur_id.with_context(date=date_new).compute(ins.late_fee, loan.company_id.currency_id)
#                 else:
#                     pri += ins.outstanding_prin
#                     intr += ins.outstanding_int
#                     fees += ins.outstanding_fees
#                     late_fees += ins.late_fee
#
#         data = [{'value': pri, 'label': 'Principle'},
#                 {'value': intr, 'label': 'Interest'},
#                 {'value': fees, 'label': 'Fees'},
#                 {'value': late_fees, 'label': 'Late Fees'}
#                 ]
#         return [{'values': data, 'title': '', 'key': _('Outstanding Amount')}]

    #@api.multi
    def get_sector_datas(self):
        '''
            Called from Compute method to calculate data for sector tab
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        data = []
        sec_dict = {}
        date_new = datetime.now()
        t1 = t2 = t3 = ('Rest', 0.00)
        so = ('Rest', 0.00)
        rest_dict = {'Rest':0.00, 'Undefined':0.00}
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done']),('company_id','=',self.env.user.company_id.id)])
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state', 'in', ['partial', 'approved', 'done'])])

        for loan in loan_obj:
            dis_tot = 0.00

            if loan.disbursement_details:
                for dis in loan.disbursement_details:
                    if dis.release_number.state == 'posted':
                        for line in dis.release_number.line_ids:
                            l1 = line.credit
#                             if loan.company_id.currency_id and loan.company_id.currency_id.id != line.journal_id.currency_id.id:
#                                 dis_tot += loan.company_id.currency_id.with_context(date=date_new).compute(l1, line.journal_id.currency_id)
#                             else:
                            dis_tot += l1
#                 l1 = [line.credit  if dis.release_number.state == 'posted' for line in dis.release_number.line_ids]
#                 dis_tot += sum(l1)
            if loan.partner_id.business_industry_id:
                if loan.partner_id.business_industry_id.name in sec_dict:
                    sec_dict[loan.partner_id.business_industry_id.name] += dis_tot
                else:
                    sec_dict.update({loan.partner_id.business_industry_id.name : dis_tot})
            else:
                rest_dict['Undefined'] += dis_tot

            so = sorted(sec_dict.items(), key=lambda kv: kv[1])
            if len(so) > 0:
                t1 = so[-1]
            if len(so) > 1:
                t2 = so[-2]
            if len(so) > 2:
                t3 = so[-3]

            data = [{'value':t1[1], 'label':t1[0]},
                    {'value':t2[1], 'label':t2[0]},
                    {'value':t3[1], 'label':t3[0]}]
        if len(so) > 3:
            for item in so[:-3]:
                rest_dict['Rest'] += item[1]

        data.append({'value':rest_dict['Rest'], 'label':'Rest'})
        data.append({'value':rest_dict['Undefined'], 'label':'Undefined'})

        [graph_title, graph_key] = self._graph_title_and_key()
        return [{'values': data, 'title': graph_title, 'key': graph_key}]

    def get_amount_dict(self):
        '''
            This method is used to get disbursed amount and principal amount
            for delinquency rate tab
            params : self
            return : a dictionary that contains total disbursed amount and total principal due
        '''
        date_new = datetime.now()
        pri = 0.00
        disb = 0.00
        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state','in',['partial','approved','done']),('company_id','=',self.env.user.company_id.id)])
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state','in',['partial','approved','done'])])
        for loan in loan_obj:
            for ins in loan.installment_id:
                if ins.date:
                    if datetime.strptime(ins.date, "%Y-%m-%d") <= date_new:
                        pri += ins.due_principal
                    disb += ins.outstanding_prin
        return {'disbursed':disb,'principal':pri}

    def get_gender_dict(self):

        if not (self._uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')):
            loan_obj = self.env['account.loan'].sudo().search([('state','not in',['cancel']),('company_id','=',self.env.user.company_id.id)])
        else:
            loan_obj = self.env['account.loan'].sudo().search([('state','not in',['cancel'])])
        year = datetime.now().year
        this_year = hst_year = 0
        all_l = f_l = 0.00
        for loan in loan_obj:
            if loan.approve_date:
                appr_date = datetime.strptime(loan.approve_date, '%Y-%m-%d')
                appr_year = appr_date.year
                if appr_year == year:
                    all_l += 1.00
                if loan.partner_id.gender == 'female':
                    f_l += 1.00
                    if appr_year == year:
                        this_year +=1
                    else:
                        hst_year += 1
#             else:
#                 all_l += 1.00
        return {'cur':this_year,'his':hst_year, 'all_loan': all_l, 'female_loan':f_l}


    #@api.multi
    def get_delinquency_datas(self):
        '''
            Called from Compute method to calculate data for delinquency tab
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        amount = self.get_out_datas()
        out_prin = 0.0
        due_due = 0.0
        if amount:
            for data_line in amount[0]['values']:
                if data_line['label'] == 'Principle':
                    out_prin = data_line['value']
#                 if data_line['label'] == 'Due Prin':
#                     due_due = data_line['value']
            due_due = amount[0]['due_prin']

        try:
            self.delinquency_percent = round((due_due / out_prin ) * 100, 2)
        except ZeroDivisionError:
            self.delinquency_percent = 0.0

        data = [{'value': due_due, 'label': 'Total Principal Due'},
                {'value': out_prin, 'label':'Total Principal Outstanding'}
                ]
        return [{'values': data, 'title': '', 'key': _('Principal Amount')}]


    #@api.multi
    def get_par_datas(self):
        '''
            Called from Compute method to calculate data for delinquency tab
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        amount = self.get_out_datas()
        out_prin = 0.0
        due_due = 0.0
        if amount:
            for data_line in amount[0]['values']:
                if data_line['label'] == 'Principle':
                    out_prin = data_line['value']
#                 if data_line['label'] == 'Due Prin':
#                     due_due = data_line['value']
            due_due = amount[0]['par_30']

        try:
            self.par_percent = round((due_due / out_prin ) * 100, 2)
        except ZeroDivisionError:
            self.par_percent = 0.0

        data = [{'value': due_due, 'label': 'Total Principal Due'},
                {'value': out_prin, 'label':'Total Principal Outstanding'}
                ]
        return [{'values': data, 'title': '', 'key': _('Principal Amount')}]


    #@api.multi
    def get_gender_datas(self):
        '''
            Called from Compute method to calculate data for gender(women)
            params : self
            return : a list of dictionary that needs to be dumped into JSON format
        '''
        amount = self.get_gender_dict()

        data = [
                {'value': amount['his'], 'label':'Past Years'},
                {'value': amount['cur'], 'label': 'Current Year'}
                ]
        return [{'values': data, 'title': '', 'key': _('Women owners')}]

    #@api.multi
    def _get_gender_percent(self):
        '''
            a compute method that calculates the gender percentage and assigns
            to delinquency_percent
            params : self
        '''
        gen = self.get_gender_dict()
        for rec in self:
            try:
                rec.gender_percent = round((float(gen['cur'])/float(gen['all_loan']))*100,2)
            except ZeroDivisionError:
                rec.gender_percent = 0
