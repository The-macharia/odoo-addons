from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleCouponApplyCode(models.TransientModel):
    _inherit = 'sale.coupon.apply.code'

    allow_switch = fields.Boolean(string='Allow switch')

    product_id = fields.Many2one(
        'product.product', string='Coupon Product')
    product_to_switch_id = fields.Many2one(
        'product.product', string='Product To Switch')

    def process_coupon(self):
        """
        Apply the entered coupon code if valid, raise an UserError otherwise.
        """
        sales_order = self.env['sale.order'].browse(
            self.env.context.get('active_id'))
        error_status = self.apply_coupon(sales_order, self.coupon_code)
        if error_status.get('error', False):
            raise UserError(error_status.get('error', False))
        if error_status.get('not_found', False):
            raise UserError(error_status.get('not_found', False))

        if self.allow_switch:
            if self.product_id and self.product_to_switch_id:
                code = self.env['coupon.program'].search(
                    [('promo_code', '=', self.coupon_code), ('active', '=', True)])

                order_line = sales_order.order_line.filtered(
                    lambda x: x.product_id == self.product_id)

                if not order_line:
                    raise UserError(
                        'Selected Coupon Product does not exist in the order!')
                curr_quantity = order_line[0].product_uom_qty

                sales_order.order_line = [(0, 0, {
                    'product_id': self.product_to_switch_id.id,
                    'product_uom_qty': curr_quantity
                })]
                sales_order.order_line = [(3, order_line[0].id, 0)]

                reward_line = sales_order.order_line.filtered(
                    lambda x: x.is_reward_line)
                if reward_line and code.reward_type == 'discount':
                    reward_line.price_unit = self.product_to_switch_id.lst_price * \
                        curr_quantity * (code.discount_percentage / 100)
