""" Python webservice to fetch invoice ID , User ID and Invoice Amount and pass it to ESD for kra signing purposes """
import os
import secrets
import sys
from flask import Flask, request
import win32print
import win32api
from waitress import serve

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():
    return secrets.token_urlsafe()


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    invoice_id = request.args.get('invoice_id')
    amount = float(request.args.get('amount'))
    """Pass invoice id and invoice tax amount to esd for signing and return the sign"""
    # default_path = os.path.join(Path.home(), 'Documents')
    invoice_file = invoice_id.replace('/', '_') + '.txt'
    invoice_file_path = os.path.join(os.getcwd(), invoice_file)
    with open(invoice_file_path, 'w+') as f:
        f.write("Invoice Id" + "\t" + "Amount" + "\n")
        f.write(invoice_id + "\t" + str(amount))

    printer_name = win32print.GetDefaultPrinter()
    res = win32api.ShellExecute(
        0, 'print', invoice_file_path, f'"{printer_name}"', None, 0)
    return str(res)


if __name__ == '__main__':
    # app.run(debug=True)
    serve(app, host='0.0.0.0', port=5000)
