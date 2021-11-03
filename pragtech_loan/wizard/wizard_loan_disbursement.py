from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, Warning

class set_loan_disbursement_amt(models.TransientModel):

    _name = "loan.disbursement.wizard"

    disbursement_amt = fields.Monetary("Amount To be disbursed", digits=(10,2), required=True)
    name = fields.Char("* ")
    date = fields.Date("Date", default = fields.datetime.today())
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

    def check_dates(self):
        approve = fields.Date.from_string(self.approve_date)
        disburse = fields.Date.from_string(self.date)
        if disburse >= approve:
            raise ValidationError(_("Disbursement date should be greater or equal to the approval date."))

    @api.model
    def default_get(self, fields):

        res = super(set_loan_disbursement_amt, self).default_get(fields)
        active_id = self._context.get('active_id')
        acc_loan = self.env['account.loan'].browse(active_id)
        total_amt = 0
        disburse_amt = 0

        if acc_loan.disbursement_details:
            for line in acc_loan.disbursement_details:
                total_amt += float(line.disbursement_amt)

        if total_amt < acc_loan.approve_amount:
            disburse_amt = acc_loan.loan_amount - total_amt
        elif not total_amt:
            disburse_amt = acc_loan.loan_amount

        res.update({
            'disbursement_amt': disburse_amt,

          })
        if acc_loan.journal_disburse_id:
            res.update({'journal_id':acc_loan.journal_disburse_id.id})
        return res


    @api.onchange('journal_id')
    def _onchange_disburse_journal(self):
        if self.journal_id:
            active_id = self._context.get('active_id')
            acc_loan = self.env['account.loan'].browse(active_id)
            self.currency_id = self.journal_id.currency_id or acc_loan.company_id.currency_id



    @api.onchange('disbursement_amt', 'currency_id')
    def _onchange_disburse_amount(self):
        journal_types = ['bank', 'cash']
        domain_on_types = [('type', 'in', list(journal_types))]

        journal_domain = []
        if not self.journal_id:
            if self.journal_id.type not in journal_types:
                self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        else:
            journal_domain = journal_domain.append(('id', '=', self.journal_id.id))

        return {'domain': {'journal_id': journal_domain}}

    ## for Extended period ........................
    def generate_lines_by_sanctioned_loan(self, acc_loan):

        move_id = None
        total_amt = 0.0
        # if self.disbursement_amt:
        #     for line in acc_loan.disbursement_details:
        #         total_amt += float(line.disbursement_amt)

        # if acc_loan.loan_amount-total_amt < self.disbursement_amt and not self._context.get('is_extended'):
        #     raise UserError("Warning : Disbursement amount can not be greater than %s"% str(acc_loan.loan_amount-total_amt))
        total_amt += self.disbursement_amt
        currency_id = self.currency_id
        if acc_loan.loan_type.calculation == 'reducing' and self._context.get('is_extended'):
            move_id = acc_loan.with_context({'is_extended': True, 'date': self._context.get('date')})._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and self._context.get('is_extended'):
            move_id = acc_loan.with_context({'is_extended': True, 'date': self._context.get('date')})._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'cnt_prin' and self._context.get('is_extended'):
            move_id = acc_loan.with_context({'is_extended': True, 'date': self._context.get('date')})._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and not acc_loan.installment_id:
                move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)
        elif acc_loan.loan_type.calculation == 'reducing' and  not acc_loan.installment_id:
            move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and acc_loan.installment_id:
            move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'reducing' and acc_loan.installment_id:
            move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'cnt_prin' and  not acc_loan.installment_id:
            move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        if total_amt >= acc_loan.approve_amount:
            acc_loan.write({'state':'approved'})
        else:
            acc_loan.write({'state':'partial'})
        if not self._context.get('is_extended'):
            self.env['account.loan.disbursement'].create({
                'name' : acc_loan.partner_id and acc_loan.partner_id.id,
                'bill_date' : self.date,
                'disbursement_amt' : self.disbursement_amt,
                'loan_id' : acc_loan.id,
                'release_number': move_id.id
                })

        for line in move_id.line_ids:
            acc_loan.write({'move_id':[(4,line.id)]})

        return True

    #@api.multi
    def approve_loan(self):
        active_id = self._context.get('active_id')
        acc_loan = self.env['account.loan'].browse(active_id)
        total_amt = 0
        currency_id = self.currency_id
        move_id = None
        total_amt = 0
        ##check approve date with disburse date ............
        if acc_loan.approve_date:
            approve_date = datetime.strptime(str(acc_loan.approve_date), "%Y-%m-%d")
            disburse_date = datetime.strptime(str(self.date), "%Y-%m-%d")
            if disburse_date < approve_date:
                raise Warning("Disbursement date can not be less than Sanctioned Date.")
        if acc_loan.disbursement_details:
            for line in acc_loan.disbursement_details:
                total_amt += float(line.disbursement_amt)

        sum_of_disburse = total_amt + self.disbursement_amt
        limit_amt = self.env.user.loan_disbursement_limit
        if sum_of_disburse > 0.0 and currency_id.id != acc_loan.company_id.currency_id.id:
            sum_of_disburse = acc_loan.company_id.currency_id.with_context(date=self.date).compute(sum_of_disburse, currency_id)
            limit_amt = acc_loan.company_id.currency_id.with_context(date=self.date).compute(limit_amt, currency_id)

        if sum_of_disburse > limit_amt:
            raise Warning("You can not disburse beyond %s %s"%(limit_amt, self.currency_id.symbol))

        if acc_loan.repayment_basis == 'sanctioned_amt':
            self.generate_lines_by_sanctioned_loan(acc_loan)
            return True
        # if self.disbursement_amt:
        #     for line in acc_loan.disbursement_details:
        #         total_amt += float(line.disbursement_amt)

        # if acc_loan.loan_amount-total_amt < self.disbursement_amt and not self._context.get('is_extended'):
        #     raise UserError("Warning : Disbursement amount can not be greater than %s"% str(acc_loan.loan_amount-total_amt))
        if not self._context.get('is_extended'):
            total_amt += self.disbursement_amt
        if acc_loan.loan_type.calculation == 'reducing' and self._context.get('is_extended'):
            move_id = acc_loan.with_context({'is_extended': True, 'date': self._context.get('date')})._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, total_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and self._context.get('is_extended'):
            move_id = acc_loan.with_context({'is_extended': True, 'date': self._context.get('date')})._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, total_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'cnt_prin' and self._context.get('is_extended'):
            move_id = acc_loan.with_context({'is_extended': True, 'date': self._context.get('date')})._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, total_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and not acc_loan.installment_id:
                move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)
        elif acc_loan.loan_type.calculation == 'reducing' and  not acc_loan.installment_id:
            move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and acc_loan.installment_id:
            move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'reducing' and  acc_loan.installment_id:
            move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)
        elif acc_loan.loan_type.calculation == 'cnt_prin' and  acc_loan.installment_id:
            move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'cnt_prin' and  not acc_loan.installment_id:
            move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)


#             elif acc_loan.loan_type.calculation == 'flat' and acc_loan.installment_id:
#                 move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt)
#
#             else:
#                 move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt)





#         def make_voucher(loan):
# #             print"\n\n\n\n LOAN >>>>>> ",loan
#             b = loan.partner_id.property_account_payable_id.id
#
#             inv = {
#                 'name': loan.name,
#                 'loan_id':loan.id,
#                 # 'name': loan.name,
#                 'voucher_type':'sale',
#                 'account_id': b,
#                 'narration': loan.name,
#                 'partner_id':loan.partner_id.id,
# #                 'payment_ids': [(6,0,create_ids)],
#             }
#             inv_obj = self.env['sale.coupon']
#             inv_id = inv_obj.create(inv)
#
# #             create_ids=[]
#             inv_ids = self.env['sale.coupon.line'].create({
# #                     'partner_id':loan.partner_id.id,
#                     'name': loan.name,
# #                     'amount':loan.approve_amount,
#                     'account_id':loan.bank_acc.id,
# #                     'type':'dr',
#                     'voucher_id':inv_id.id,
#                     'price_unit':self.disbursement_amt,
#
#             })
# #             create_ids.append(inv_id)
#             acc_loan.write({'voucher_id': inv_id.id})
#
#             inv_id.proforma_voucher()
#             return inv_id

#         res = make_voucher(acc_loan)

#         print("\n\n\n\n\n",res)
        if total_amt >= acc_loan.approve_amount:
            acc_loan.write({'state':'approved'})
        else:
            acc_loan.write({'state':'partial'})
        disburse_id = False
        if not  self._context.get('is_extended'):
            disburse_id = self.env['account.loan.disbursement'].create({
                'name' : acc_loan.partner_id and acc_loan.partner_id.id,
                'bill_date' : self.date,
                'disbursement_amt' : self.disbursement_amt,
                'loan_id' : acc_loan.id,
                'release_number': move_id.id
                })

        for line in move_id.line_ids:
            acc_loan.write({'move_id':[(4,line.id)]})

        return disburse_id


    def generate_lines_by_sanctioned_loan_old(self, acc_loan):

        move_id = None
        total_amt = 0.0
        # if self.disbursement_amt:
        #     for line in acc_loan.disbursement_details:
        #         total_amt += float(line.disbursement_amt)

        # if acc_loan.loan_amount-total_amt < self.disbursement_amt:
        #     raise UserError("Warning : Disbursement amount can not be greater than %s"%float(acc_loan.loan_amount-total_amt))
        total_amt += self.disbursement_amt
        currency_id = self.currency_id
        if acc_loan.loan_type.calculation == 'flat' and not acc_loan.installment_id:
                move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)
        elif acc_loan.loan_type.calculation == 'reducing' and  not acc_loan.installment_id:
            move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and acc_loan.installment_id:
            move_id = acc_loan.with_context(self._context)._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        else:
            move_id = acc_loan.with_context(self._context)._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)

        if total_amt >= acc_loan.approve_amount:
            acc_loan.write({'state':'approved'})
        else:
            acc_loan.write({'state':'partial'})

        if move_id:
            self.env['account.loan.disbursement'].create({
                'name' : acc_loan.partner_id and acc_loan.partner_id.id,
                'bill_date' : self.date,
                'disbursement_amt' : self.disbursement_amt,
                'loan_id' : acc_loan.id,
                'release_number': move_id.id
                })

            for line in move_id.line_ids:
                acc_loan.write({'move_id':[(4,line.id)]})

        return True

    #@api.multi
    def approve_loan_old(self):
        active_id = self._context.get('active_id')
        acc_loan = self.env['account.loan'].browse(active_id)

        total_amt = 0
        disburse_id = None
        currency_id = self.currency_id
        move_id = None
        if datetime.strptime(str(self.date), "%Y-%m-%d") < datetime.strptime(str(acc_loan.approve_date), "%Y-%m-%d"):
            date_in_date = datetime.strptime(str(acc_loan.approve_date), "%Y-%m-%d")
            date_appr = datetime.strftime(date_in_date, "%m/%d/%Y")
            raise Warning("Disbursement date can not be less than %s "%date_appr)
        if acc_loan.repayment_basis == 'sanctioned_amt':
            self.generate_lines_by_sanctioned_loan(acc_loan)
            return True
        # if self.disbursement_amt:
        #     for line in acc_loan.disbursement_details:
        #         total_amt += float(line.disbursement_amt)

        # if acc_loan.loan_amount-total_amt < self.disbursement_amt:
        #     raise UserError("Warning : Disbursement amount can not be greater than %s"%(acc_loan.loan_amount-total_amt))

        total_amt += self.disbursement_amt
        if acc_loan.loan_type.calculation == 'flat' and not acc_loan.installment_id:
                move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)
        elif acc_loan.loan_type.calculation == 'reducing' and  not acc_loan.installment_id:
            move_id = acc_loan._simple_interest_get_by_disbursed(acc_loan.interest_rate, total_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)

        elif acc_loan.loan_type.calculation == 'flat' and acc_loan.installment_id:
            move_id = acc_loan.with_context(self._context)._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, disburse_date=self.date, currency_id = currency_id, journal_id = self.journal_id)
        else:
            move_id = acc_loan.with_context(self._context)._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt, self.date, currency_id = currency_id, journal_id = self.journal_id)


#             elif acc_loan.loan_type.calculation == 'flat' and acc_loan.installment_id:
#                 move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt)
#
#             else:
#                 move_id = acc_loan._get_simple_int_by_existed_disbursed(acc_loan.interest_rate, self.disbursement_amt)





#         def make_voucher(loan):
# #             print"\n\n\n\n LOAN >>>>>> ",loan
#             b = loan.partner_id.property_account_payable_id.id
#
#             inv = {
#                 'name': loan.name,
#                 'loan_id':loan.id,
#                 # 'name': loan.name,
#                 'voucher_type':'sale',
#                 'account_id': b,
#                 'narration': loan.name,
#                 'partner_id':loan.partner_id.id,
# #                 'payment_ids': [(6,0,create_ids)],
#             }
#             inv_obj = self.env['sale.coupon']
#             inv_id = inv_obj.create(inv)
#
# #             create_ids=[]
#             inv_ids = self.env['sale.coupon.line'].create({
# #                     'partner_id':loan.partner_id.id,
#                     'name': loan.name,
# #                     'amount':loan.approve_amount,
#                     'account_id':loan.bank_acc.id,
# #                     'type':'dr',
#                     'voucher_id':inv_id.id,
#                     'price_unit':self.disbursement_amt,
#
#             })
# #             create_ids.append(inv_id)
#             acc_loan.write({'voucher_id': inv_id.id})
#
#             inv_id.proforma_voucher()
#             return inv_id

#         res = make_voucher(acc_loan)

#         print("\n\n\n\n\n",res)
        if total_amt >= acc_loan.approve_amount:
            acc_loan.write({'state':'approved'})
        else:
            acc_loan.write({'state':'partial'})
        if move_id:
            disburse_id = self.env['account.loan.disbursement'].create({
                'name' : acc_loan.partner_id and acc_loan.partner_id.id,
                'bill_date' : self.date,
                'disbursement_amt' : self.disbursement_amt,
                'loan_id' : acc_loan.id,
                'release_number': move_id.id
                })

            for line in move_id.line_ids:
                acc_loan.write({'move_id':[(4,line.id)]})

        return disburse_id
