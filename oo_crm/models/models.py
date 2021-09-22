from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    region_id = fields.Many2one('crm.region', string='Region')
    territory_id = fields.Many2one('crm.region.territory', string='Territory')
    subterritory_id = fields.Many2one(
        'crm.region.subterritory', string='Sub Territory')


class CrmRegion(models.Model):
    _name = 'crm.region'

    name = fields.Char(required=True)


class CrmRegionTerritory(models.Model):
    _name = 'crm.region.territory'

    name = fields.Char(required=True)
    region_id = fields.Many2one('crm.region', string='Region', required=True)


class CrmRegionSubTerritory(models.Model):
    _name = 'crm.region.subterritory'

    name = fields.Char(required=True)
    territory_id = fields.Many2one(
        'crm.region.territory', string='Territory', required=True)

    region_id = fields.Many2one(
        related='territory_id.region_id', string='Region')
