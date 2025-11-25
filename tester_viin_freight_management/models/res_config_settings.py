from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_sale_account_analytic_suffix = fields.Boolean(
        related='company_id.custom_sale_account_analytic_suffix',
        readonly=False)
    shipment_cargo_mode = fields.Selection(
        related='company_id.shipment_cargo_mode',
        readonly=False)
    prevent_unlink_sales_having_transport_related = fields.Boolean(
        related='company_id.prevent_unlink_sales_having_transport_related',
        readonly=False)
