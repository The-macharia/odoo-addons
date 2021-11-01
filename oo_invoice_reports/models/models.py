from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    goods_nature = fields.Char(string='Nature of Goods')
    hawb = fields.Char(string='HAWB')
    mawb = fields.Char(string='MAWB')
    no_of_packages = fields.Integer(string='No of Packages')
    flight = fields.Char(string='Flight')
    cbm = fields.Char(string='CBM')
    total_kgs = fields.Float(string='KGS')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    goods_nature = fields.Char(string='Nature of Goods')
    hawb = fields.Char(string='HAWB')
    mawb = fields.Char(string='MAWB')
    no_of_packages = fields.Integer(string='No of Packages')
    flight = fields.Char(string='Flight')
    cbm = fields.Char(string='CBM')
    total_kgs = fields.Float(string='KGS')

    def _prepare_invoice(self):
        self.ensure_one()
        res = super()._prepare_invoice()
        res.update({
            'cbm': self.cbm,
            'hawb': self.hawb,
            'goods_nature': self.goods_nature,
            'no_of_packages': self.no_of_packages,
            'total_kgs': self.total_kgs,
            'flight': self.flight,
            'mawb': self.mawb,
        })

        return res
