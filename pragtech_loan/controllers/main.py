from odoo import http
from odoo.http import request, Response
import json
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class LoanApplication(http.Controller):
        @http.route('/api/create_loan',auth='user',type='json',csrf=False,method=['POST'])
        def create_payment(self, **kw):
            print(http.request)
            print(self,kw)
            data = json.loads(request.httprequest.data)
            print(data,"TESTING FORMAT")
            new_loan_request  = http.request.env['account.loan'].sudo().create(data)
            print(new_loan_request,"DDDDDDDDDDDDDDDDDDDDAAAAAAAAAAAAAAAAAAAAAAAAATTTTTTTTTTTTTTTTAAAAAAAAAAAAAAA")
            args = {'success': True, 'message': 'Success', 'id': data}
            args2 = {'unsuccess': False, 'message': 'UnSuccess', 'id': data}
            if new_loan_request:
                return args
            else:
                return args2
        @http.route('/api/single_loan',auth='user',type="json", method=['POST'])
        def get_loan_details(self,loan_id=None):
            data = json.loads(request.httprequest.data)
            print(data)
            if data['loan_id']:
                domain = [('loan_id', '=', data['loan_id'])]
                loans_rec = request.env['account.loan'].search(domain)
                print("TESTING FIELDS")
                repay_rec = request.env['account.loan'].sudo().search([('id','=',loans_rec.id)]).mapped('installment_id').filtered(lambda r: r.state != 'paid')
                if loans_rec.state == 'kiva_loan':
                    loan_repo4=[]
                    data = repay_rec[0]
                    response4={
                        'Id':loans_rec['id'],
                        'Partner_id': loans_rec.partner_id['name'],
                        'Loan Amount':loans_rec['loan_amount'],
                        'Due Amount': data.due_principal,
                        'Due Date':data.date,
                        'Loan State':loans_rec.state,
                        "Loan Id":loans_rec.loan_id }
                    loan_repo4.append(response4)
                    data34= {'status': 200, 'response': loan_repo4, 'message': 'Loan Informations'}
                    return data34
                elif loans_rec.state == 'p_scheduled':
                    loan_repo3=[]
                    data = repay_rec[0]
                    response3={
                        'Id':loans_rec['id'],
                        'Partner_id': loans_rec.partner_id['name'],
                        'Loan Amount':loans_rec['loan_amount'],
                        'Due Amount': data.due_principal,
                        'Due Date':data.date,
                        'Loan State':loans_rec.state,
                        "Loan Id":loans_rec.loan_id }
                    loan_repo3.append(response3)
                    data33 = {'status': 200, 'response': loan_repo3, 'message': 'Loan Informations'}
                    return data33
                    
                elif loans_rec.state == 'approved':
                    loan_repo2=[]
                    data = repay_rec[0]
                    response2={
                        'Id':loans_rec['id'],
                        'Partner_id': loans_rec.partner_id['name'],
                        'Loan Amount':loans_rec['loan_amount'],
                        'Due Amount': data.due_principal,
                        'Due Date':data.date,
                        'Loan State':loans_rec.state,
                        "Loan Id":loans_rec.loan_id }
                    loan_repo2.append(response2)
                    data32 = {'status': 200, 'response': loan_repo2, 'message': 'Loan Informations'}
                    return data32

                else:
                    loan_repo1=[]
                    response1={
                        'Id':loans_rec['id'],
                        'Partner_id': loans_rec.partner_id['name'],
                        'Loan Amount':loans_rec['loan_amount'],
                        # 'Due Amount': data.due_principal,
                        # 'Due Date':data.date,
                        'Loan State':loans_rec.state,
                        "Loan Id":loans_rec.loan_id }
                    loan_repo1.append(response1)
                    data31= {'message': 'This Loan Has not been Approved Yet','response': loan_repo1,'status_code': 302}
                    return data31


                    
            
            
            #  {
            #     "Id": 1874,
            #     "Partner_id": "Djamilla Mukamana",
            #     "Loan Amount": 2000000.0,
            #     "Due Amount": 0.0,
            #     "Due Date": "2021-01-30",
            #     "Loan State": "approved",
            #     "Loan Id": "LOAN/4582/2021"
            # } 


        @http.route('/create_payments',auth='user',type='json',csrf=False,method=['POST'])
        def create_payment(self, **kw):
          print(http.request)
          print(self,kw)
          data = json.loads(request.httprequest.data)
          print(data,"TESTING FORMAT")
          new_payment_request  = http.request.env['account.loan.repayment'].sudo().create(data)
          print(new_payment_request,"DDDDDDDDDDDDDDDDDDDDAAAAAAAAAAAAAAAAAAAAAAAAATTTTTTTTTTTTTTTTAAAAAAAAAAAAAAA")
          args = {'success': True, 'message': 'Success', 'id': data}
          args2 = {'unsuccess': False, 'message': 'UnSuccess', 'id': data}
          if new_payment_request:
              return args
          else:
              return args2
          
          
       
          

        @http.route(['/api/get_loan_data', '/get_loan_data/<int:loan_id>'], type='json', auth='user')
        def get_loans(self, loan_id=None):
            # if self.state == 'p_scheduled':
            if loan_id:
                domain = [('id', '=', loan_id)]
            else:
                domain = []
            loans_rec = request.env['account.loan'].search(domain)
            loans = []
            for rec in loans_rec:
                repay_rec = request.env['account.loan'].sudo().search([('id','=',rec.id)]).mapped('installment_id').filtered(lambda r: r.state != 'paid')
                # data = repay_rec[0].due_principal
                vals = {
                    'Id': rec.id,
                    'Name': rec.name,
                    'Partner_id': rec.partner_id.name,
                    # 'Due amount' : data,
                    # "Loan Status":rec.status,
                    'Approved_amount': rec.approve_amount,
                    'State' : rec.state,
                    'Stage_id' : rec.stage_id.name,
                }
                loans.append(vals)
                data = {'status': 200, 'response': loans, 'message': 'Single Loan Information'}
        # else:
        #     data = {'status': 100,'message': 'This Loan Has not been Approved'}
        # #   (new_partner_id,'kadweka')

        @http.route('/api/get_loan', type='json', auth='user')
        def get_all_loans(self):
            date_today = datetime.today().strftime('%Y-%m-%d')
            loan_rec = request.env['account.loan'].sudo().search([])
            # print(loan_rec.loan_id,"KADWEKA KATANA")
            loans=[]
            for rec in loan_rec:
              repay_rec = request.env['account.loan'].sudo().search([('id','=',rec.id)]).mapped('installment_id').filtered(lambda r: r.state != 'paid')
              partner_rec = request.env['account.loan'].sudo().search([('id','=',rec.id)]).mapped('partner_id').filtered(lambda r: r.name)
              print(partner_rec)
              if repay_rec:
                data = repay_rec[0].due_principal
                print(data,'repayment')
                vals={
                    'Id':rec.id,
                    'name':rec.name,
                    'Loan_id':rec.loan_id,
                    "Partner":rec.partner_id.name,
                    'Currency':rec.partner_id.currency_name,
                    'Loan Amount':rec.loan_amount,
                    'Due Amount': data,
                    'Date':date_today
                    }
                loans.append(vals)
            print('LOAN LIST',date_today)
            data = {"status": 200,'response':loans,'message':'All Loans Returned'}
            return data
        
        # @http.route('/api/create_loan',auth='user',type='json',csrf=False,method=['POST'])
        # def create_loan(self, **kw):
        #   print(http.request)
        #   print(self,kw)
        #   data = json.loads(request.httprequest.data)
        #   print(data,"TESTING FORMAT")
        #   new_loan_request  = http.request.env['account.loan'].sudo().create(data)
        #   print(new_loan_request,"DDDDDDDDDDDDDDDDDDDDAAAAAAAAAAAAAAAAAAAAAAAAATTTTTTTTTTTTTTTTAAAAAAAAAAAAAAA")
        #   args = {'success': True, 'message': 'Loan Created Successfully', 'id': data}
        #   args2 = {'unsuccess': False, 'message': 'UnSuccess', 'id': data}
        #   if new_loan_request:
        #       return args
        #   else:
        #       return args2
