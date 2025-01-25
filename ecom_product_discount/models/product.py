# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_percentage = fields.Float(
        string='Discount(%)'
    )
    discounted_product_price = fields.Float(
        string='Discounted Product Price',
        compute='_compute_disc_product_price',
        store=True
    )

    @api.depends('discount_percentage', 'list_price')
    def _compute_disc_product_price(self):
        for product in self:
            if product.discount_percentage > 100:
                raise ValidationError(_('You cannot enter more than 100.'))
            discount = (product.list_price * product.discount_percentage) / 100
            if discount:
                product.discounted_product_price = product.list_price - discount
            else:
                product.discounted_product_price = 0.0

    def _get_sales_prices(self, pricelist, fiscal_position):
        vals = super()._get_sales_prices(pricelist, fiscal_position)
        for product in self:
            if product.discounted_product_price:
               price_dtls = vals[product.id]
               price_dtls['price_reduce'] = product.discounted_product_price
        return vals

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1.0,
        parent_combination=False, only_template=False,
    ):
        vals = super()._get_combination_info(
            combination=combination, product_id=product_id,
            add_qty=add_qty, parent_combination=parent_combination,
            only_template=only_template
        )
        product_id = self.env['product.product'].sudo().browse(vals.get('product_id'))
        if product_id.discounted_product_price:
            vals['has_discounted_price'] = True
            vals['price'] = product_id.discounted_product_price
            vals['base_unit_price'] = product_id.discounted_product_price
        return vals

    def _get_additionnal_combination_info(
        self, product_or_template,
        quantity, date, website
    ):
        vals = super()._get_additionnal_combination_info(
            product_or_template, quantity, date, website
        )
        if product_or_template.discounted_product_price:
            vals['has_discounted_price'] = True
            vals['price'] = product_or_template.discounted_product_price
            vals['base_unit_price'] = product_or_template.discounted_product_price
        return vals
