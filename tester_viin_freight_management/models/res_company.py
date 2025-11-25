from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    custom_sale_account_analytic_suffix = fields.Boolean(
        string='Custom Sale Account Analytic Suffix',
        help="If enabled, will display the shipment name alongside the analytic account name in reports and dropdowns. "
            "Example: SO0001 displays as 'SO0001 - SHP0001'")
    shipment_cargo_mode = fields.Selection(selection=[
        ('simple_note', 'Quick Note Entry'),
        ('structured_entry', 'Detailed Structured Entry'),
    ], string='Cargo Input Mode', default='simple_note',
        help="Specify how to input cargo information for this shipment:\n\n"
        "- Quick Note Entry: Allows you to enter a free-style text description of the cargo. "
        "Suitable for large or simple shipments where detailed breakdown (e.g., per pallet, per item) is not required.\n"
        "- Detailed Structured Entry: Enables full cargo structuring including packages, containers, individual items, "
        "HS Codes, and dangerous goods classification.\n"
        "Recommended for international shipments or when detailed documentation (e.g., for B/L) is needed.")
    prevent_unlink_sales_having_transport_related = fields.Boolean(
        string='Prevent Unlink Sales Having Transport Related',
        help="If enabled, will prevent unlinking sales order lines that have a shipment, route or booking linked to them.")
