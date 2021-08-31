from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fine_amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one(
        'ke.deductions.type', string='Deduction Type')
    rule_id = fields.Many2one(
        related='deduction_id.rule_id', string="Salary Rule")
    overtime_hours = fields.Float(string='Overtime Hours')
    contract_id = fields.Many2one('hr.contract', string='Contract')


class HrContract(models.Model):
    _inherit = 'hr.contract'

    cash_allowance_id = fields.Many2one(
        'ke.cash.allowances.type', string='Allowance Type')
    allowance_amount = fields.Float(string='Amount')

    rule_id = fields.Many2one(string='Salary Rule',
                              related='cash_allowance_id.rule_id')

    @api.model
    def contract_expiry(self):
        expiry_date = datetime.now().date() + timedelta(days=14)

        for rec in self.search([('state', 'in', ['open'])]):
            if rec.date_end and rec.employee_id.parent_id:
                if expiry_date == rec.date_end:

                    mail_content = "Hello  " + rec.employee_id.parent_id.name + ",<br>Your employee " + \
                        rec.employee_id.name + \
                        "contract is going to expire in 14 Days. Please review it and possibly renew."

                    main_content = {
                        'subject': _('%s Contract Expiry') % (rec.employee_id.name),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': rec.employee_id.parent_id.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()

                    rec.update({'state': 'pending'})


class KeCashAllowanceType(models.Model):
    _inherit = 'ke.cash.allowances.type'

    is_recurring = fields.Boolean(
        string='Recurring Allowance', help='This type of allowance is recurrent every month.')


class KeDeductionType(models.Model):
    _inherit = 'ke.deductions.type'

    is_recurring = fields.Boolean(
        string='Recurring Deduction', help='This type of deduction is recurrent every month.')


class KeBatchDeduction(models.Model):
    _name = 'ke.batch.deduction'
    _description = 'Batch Deduction Allocation'

    @api.multi
    def action_confirm_deductions(self):
        if len(self.deduction_ids) == 0:
            raise ValidationError(
                'You must have atleast one employee selected to continue with this operation!')
        else:
            for rec in self.deduction_ids:
                vals = {
                    'deduction_id': rec.deduction_type_id.id,
                    'computation': 'fixed',
                    'fixed': rec.amount,
                    'employee_id': rec.employee_id.id,
                }
                self.env['ke.deductions'].sudo().create(vals)
            self.write({'state': 'confirm'})

    name = fields.Char(string='Brief Title', required=True)
    note = fields.Text(string='Note')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    deduction_ids = fields.One2many(
        'ke.batch.deduction.ids', 'deduction_id', string='Deduction Ids')
    details = fields.Html(string='Details')


class KeBatchDeductionIds(models.Model):
    _name = 'ke.batch.deduction.ids'
    _description = 'Batch Deduction Ids'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)
    deduction_type_id = fields.Many2one(
        'ke.deductions.type', string='Deduction Type', required=True)
    rule_id = fields.Many2one(
        related='deduction_type_id.rule_id', string="Salary Rule")
    amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one('ke.batch.deduction', string='Deduction Id')
    reason = fields.Text(string='Reason')
