# -*- coding: utf-8 -*-

from odoo import models, fields
import openpyxl as XL
import base64
from openpyxl.styles import Alignment, Font, numbers
from openpyxl.utils import get_column_letter
import os
import tempfile
from datetime import date


class AnalyticReport(models.TransientModel):
    _name = 'analyic.report.wizard'
    _description = 'Generate analytic account wizards'

    period = fields.Selection(string='Timeframe', selection=[(
        'today', 'Today'), ('month', 'This Month'), ('between', 'Custom Dates')])
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')

    def generate_report(self):
        return True
