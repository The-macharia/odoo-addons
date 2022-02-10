from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError

from collections import OrderedDict

from odoo.addons.payments_equity.controllers.main import PaymentsEquity
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing


@tagged('post_install', '-at_install')
class EquityPaymentAcquirer(TransactionCase):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super(EquityPaymentAcquirer, cls).setUpClass()

        cls.data = OrderedDict([
            ('soapenv:Envelope', OrderedDict([
                ('@xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/'), 
                ('@xmlns:ns1', 'http://EquitySTKkenya.integration.mb.modefinserver.com/'), 
                ('soapenv:Header', OrderedDict([
                    ('username', 'cake'), 
                    ('password', 'parm')])), 
                    ('soapenv:Body', OrderedDict([
                        ('ns1:paymentConfirmation', OrderedDict([
                            ('TillNumber', '123456'), 
                            ('mobileNumber', '2547655540042'), 
                            ('amount', '2000'), 
                            ('timeStamp', '1643546822'), 
                            ('transactionRefNo', '100000127474'), 
                            ('servedBy', 'Muriuki'), 
                            ('additionalInfo', 'Cake')]))]))]))])

        cls.acquirer = cls.env['payment.acquirer'].sudo().search([('provider', '=', 'equity')], limit=1)

    def test_check_credentials(self):
        confirmed_credentials, credentials_comment = PaymentsEquity.confirm_credentials(PaymentsEquity, self.acquirer, self.data)
        self.assertEqual(confirmed_credentials, True)

    def test_check_data(self):
        valid_data, payment_data, data_comment = PaymentsEquity.check_data_validity(PaymentsEquity, self.acquirer, self.data)
        self.assertEqual(valid_data, True)
        self.assertEqual(payment_data, {
            'mobile': '2547655540042',
            'amount': 2000,
            'transaction_timestamp': '1643546822',
            'acquirer_reference': '100000127474'
        })

    def test_get_partner_id(self):
        mobile = self.acquirer.check_phone(self.data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('mobileNumber', False))
        self.assertEqual(mobile, '2547655540042')
        partner_id = self.acquirer.get_partner_id(mobile)
        self.assertEqual(partner_id, 14)

    def test_get_invoices(self):
        mobile = self.acquirer.check_phone(self.data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('mobileNumber', False))
        partner_id = self.acquirer.get_partner_id(mobile)
        amount = self.data.get('soapenv:Envelope', {}).get('soapenv:Body', {}).get('ns1:paymentConfirmation', {}).get('amount', 0)
        invoices = self.acquirer.get_invoices(partner_id, int(amount))
        self.assertEqual(invoices, [(6, 0, [1])])

    def test_create_tx(self):
        tx = self.acquirer.create_tx({
            'mobile': '2547655540042',
            'amount': 2000,
            'transaction_timestamp': '1643546822',
            'acquirer_reference': '100000127474'
        })
        self.assertEqual(tx.state, 'done')
        # monitored_tx = PaymentPostProcessing.get_monitored_transaction_ids()
        # postprocess_tx = tx.id in monitored_tx
        # self.assertEqual(postprocess_tx, True)
        # self.env['payment.transaction']._cron_finalize_post_processing()
        self.assertEqual(tx.is_post_processed, True)
        self.assertEqual(tx.payment_id.payment_transaction_id.id, tx.id)
        self.assertEqual(tx.payment_id.amount, tx.amount)
        self.assertEqual(tx.invoice_ids[0].payment_state, 'partial')

    # def test_authorise_transaction(self):
    #     result_code, transaction_no = PaymentsEquity.authorise_transaction(PaymentsEquity, self.data, self.acquirer)
    #     self.assertEqual(result_code, 'Success')
    #     self.assertEqual(transaction_no, '100000127474')