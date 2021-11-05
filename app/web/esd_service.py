""" Python webservice to fetch invoice ID , User ID and Invoice Amount and pass it to ESD for kra signing purposes """
# import hug
import time
import os
import win32print
import win32api
import win32ui
import sys
from pathlib import Path
from flask import Flask, request
from subprocess import call
from ctypes import *
from win32com.client import Dispatch
import win32com.client as win32

app = Flask(__name__)
sys.path.append(os.getcwd())


# @hug.get('/esd')
@app.route('/esd',methods=['POST', 'GET'])
def esd():
    invoice_id = request.args.get('invoice_id')
    amount = float(request.args.get('amount'))
    # hllDll = ctypes.WinDLL()
    # dll_path = "C:\\Users\\B14\\Downloads\\Compressed\\ESD FILES1\\ESD extracted files after installation\\tresdlib.dll"
    # lib = WinDLL("C:\\Users\\B14\\Downloads\\Compressed\\ESD FILES1\\ESD extracted files after installation\\tresdlib.dll")
    # lib.FSL_Command("Z")
    # dll = Dispatch("tresdlib.dll")
    # dll =win32.gencache.EnsureDispatch(dll_path)
    """Pass invoice id and invoice tax amount to esd for signing and return the sign"""
    # default_path = os.path.join(Path.home(), 'Documents')
    invoice_file = invoice_id.replace('/','_') + '.txt'
    # invoice_file_path = os.path.join(invoice_file)
    with open(invoice_file, 'w+') as f:
        f.write("Invoice Id" + "\t" + "Amount" + "\n")
        f.write(invoice_id + "\t" + str(amount))
    call(['notepad', '/p', invoice_file])

    # file = "C:\\Users\\B14\\Documents\\ESD_SERVER\\MISC_001_2021.txt"
    # lib.FSL_Command('SIGN',"invoice_file")

    return 'pass'

if __name__ == '__main__':
    app.run(debug=True)