from odoo import api, fields, models, _

class EducationalLevel(models.Model):
    
    _name = 'educational.level'
    
    name = fields.Char(string="Educational Level")
    
class BusinessRegistrationStatus(models.Model):
    
    _name = 'business.registration.status'
    
    name = fields.Char(string="Name")
    
class CampDetails(models.Model):
    
    _name = 'camp.details'
    
    name = fields.Char(string="Name")
