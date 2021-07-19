import base64
import logging
import os
import tempfile

from odoo import _, api, models
from odoo.exceptions import ValidationError
from PyPDF2 import PdfFileReader, PdfFileWriter

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_send_by_email(self):
        for rec in self:
            if rec.state != 'done':
                raise ValidationError(
                    'You cannot send a payslip that has not been confirmed!')

            password = rec.employee_id.identification_id or ''
            filename = f"{(rec.name or rec.employee_id.name)}"
            pdf = self.env.ref(
                'hr_payroll.action_report_payslip').render_qweb_pdf(rec.id)

            if pdf:
                pdf_path = rec.create_pdf()
                with open(pdf_path, 'wb') as f:
                    f.write(pdf[0])

                self.add_encryption(pdf_path, password)
                pdf_id = rec.save_pdf_file(pdf_path, filename, rec.id)

                email_body = f"""
Dear {rec.employee_id.name},
<br/>
<br/>

Please Find Attached your {rec.date_to and rec.date_to.strftime('%B')} Payslip.
<br/>
The Payslip is password protected and your password is your <b>National ID number</b>.
<br/>
If you have any queries, please reach out to your Manager or the HR.
<br/>
<br/>
Best Regards
<br/>
<br/>
{rec.company_id.name}
                """

                mail_values = {
                    'model': 'hr.payslip',
                    'subject': filename,
                    'email_to': rec.employee_id.work_email,
                    'email_from': self.env.user.partner_id.email,
                    'body_html': email_body,
                    'res_id': rec.id,
                    'attachment_ids': [(6, 0, [pdf_id.id])]
                }
                email = self.env['mail.mail'].sudo().create(mail_values)
                email.send()

    @ api.model
    def create_pdf(self):
        _, pdf_path = tempfile.mkstemp(
            suffix='.pdf', prefix='pdfreport.tmp.')
        return pdf_path

    @ api.model
    def save_pdf_file(self, pdf_path, file_name, rec_id):
        attachment_id = None
        with open(pdf_path, 'rb') as f:
            attachment = {
                'name': f"{file_name}.pdf",
                'datas': base64.encodestring(f.read()),
                'res_model': 'hr.payslip',
                'res_id': rec_id,
                'mimetype': 'application/x-pdf'
            }
            try:
                attachment_id = self.env['ir.attachment'].create(attachment)
            except Exception as e:
                _logger.warning(
                    f'An error occurred while trying to save the file {attachment["name"]}')
            else:
                _logger.info(
                    'The document: %s is now saved in the database',
                    attachment['name'])
                self.delete_tempfile(pdf_path)

        return attachment_id

    @ api.model
    def delete_tempfile(self, path):
        try:
            os.unlink(path)
        except (OSError, IOError):
            _logger.error('Error when trying to remove file %s' % path)

    def add_encryption(self, input, password):
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(input)

        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

        pdf_writer.encrypt(user_pwd=password, owner_pwd=None, use_128bit=True)

        with open(input, 'wb') as f:
            pdf_writer.write(f)
