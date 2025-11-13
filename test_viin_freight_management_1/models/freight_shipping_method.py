from odoo import fields, models


class FreightShippingMethod(models.Model):
    _name = 'freight.shipping.method'
    _description = 'Freight Shipping Method'

    name = fields.Char(
        string='Name',
        required=True,
        help="Name of the shipping method (e.g., FCL, LCL, Express, Bulk)."
    )

    is_sea = fields.Boolean(
        string='Applicable for Sea',
        help="Tick if this shipping method can be used for sea freight (e.g., FCL, LCL, Bulk cargo)."
    )
    is_air = fields.Boolean(
        string='Applicable for Air',
        help="Tick if this shipping method can be used for air freight (e.g., Express, Economy, Priority)."
    )
    is_land = fields.Boolean(
        string='Applicable for Land',
        help="Tick if this shipping method can be used for land transport (e.g., FTL, LTL, Project Cargo)."
    )

    active = fields.Boolean(string='Active', default=True)
