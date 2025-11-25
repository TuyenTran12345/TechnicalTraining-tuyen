from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    direction = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ('domestic', 'Domestic')
    ], string='Direction', readonly=True)
    transport_mode = fields.Selection([
        ('sea', 'Sea Freight'),
        ('air', 'Air Freight'),
        ('land', 'Land Transport'),
        ('multiple', 'Multi-modal'),
    ], string='Transport Mode', readonly=True)
    ocean_shipping_method_id = fields.Many2one('freight.shipping.method', string='Ocean Shipping Method', readonly=True)
    air_shipping_method_id = fields.Many2one('freight.shipping.method', string='Air Shipping Method', readonly=True)
    land_shipping_method_id = fields.Many2one('freight.shipping.method', string='Land Shipping Method', readonly=True)
    shipping_method_name = fields.Char(string='Shipping Method', readonly=True)

    def _select_additional_fields(self):
        fields_select = super()._select_additional_fields()
        fields_select.update({
            'direction': 's.direction',
            'transport_mode': 's.transport_mode',
            'ocean_shipping_method_id': 's.ocean_shipping_method_id',
            'air_shipping_method_id': 's.air_shipping_method_id',
            'land_shipping_method_id': 's.land_shipping_method_id',
            'shipping_method_name': "COALESCE(ocean_sm.name, air_sm.name, land_sm.name)",
        })
        return fields_select

    def _from_sale(self):
        from_clause = super()._from_sale()
        return f"""{from_clause}
            LEFT JOIN freight_shipping_method ocean_sm ON ocean_sm.id = s.ocean_shipping_method_id
            LEFT JOIN freight_shipping_method air_sm ON air_sm.id = s.air_shipping_method_id
            LEFT JOIN freight_shipping_method land_sm ON land_sm.id = s.land_shipping_method_id
        """

    def _group_by_sale(self):
        group_by = super()._group_by_sale()
        return f"""{group_by},
            s.direction,
            s.transport_mode,
            s.ocean_shipping_method_id,
            s.air_shipping_method_id,
            s.land_shipping_method_id,
            ocean_sm.name,
            air_sm.name,
            land_sm.name
        """
