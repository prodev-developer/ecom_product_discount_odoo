# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_values(
        self, product_id, quantity, linked_line_id=False,
        no_variant_attribute_values=None, product_custom_attribute_values=None,
        **kwargs
    ):
        vals = super()._prepare_order_line_values(
            product_id, quantity, linked_line_id=False,
            no_variant_attribute_values=None, product_custom_attribute_values=None,
            **kwargs
        )
        if vals.get('product_id'):
            product_id = self.env['product.product'].sudo().browse(
                vals.get('product_id'))
            if product_id.discount_percentage:
                vals['discount'] = product_id.discount_percentage
        return vals

    def _prepare_order_line_update_values(
        self, order_line, quantity, linked_line_id=False, **kwargs
    ):
        vals = super()._prepare_order_line_update_values(
            order_line, quantity, linked_line_id=False, **kwargs
        )
        if order_line:
            product_id = order_line.product_id
            if product_id.discount_percentage:
                vals['discount'] = product_id.discount_percentage
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends(
        'product_id', 'product_uom',
        'product_uom_qty'
    )
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            if line.product_id.discount_percentage and line.order_id.website_id:
                if not line.product_id or line.display_type:
                    line.discount = 0.0
                else:
                    line.discount = line.product_id.discount_percentage
        return res
