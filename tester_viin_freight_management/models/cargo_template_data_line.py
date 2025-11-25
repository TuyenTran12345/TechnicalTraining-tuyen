from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CargoTemplateDataLine(models.Model):
    _name = 'freight.cargo.template.data.line'
    _description = 'Cargo Template Data Line'

    name = fields.Char(
        string='Description', required=True, default=lambda self: _('New'),
        help="Short description or label for the cargo commodity. Often auto-generated "
            "but can be manually updated to reflect the actual goods (e.g., 'TV 55 inch - Box 1').")

    volume_uom_name = fields.Char(string='Volume Unit of Measure', compute='_compute_volume_uom_name')
    weight_uom_name = fields.Char(string='Weight Unit of Measure', compute='_compute_weight_uom_name')

    is_individual_package = fields.Boolean(
        string='Is Individual Package',
        help="Tick if this cargo commodity is a physical package that should be tracked separately (e.g., seal, weight, etc.)"
    )
    package_type_id = fields.Many2one(
        'stock.package.type', string='Package Type',
        help="Type of packaging used for this cargo commodity (e.g., Carton, Pallet, Wooden Crate). "
            "Useful for volume estimation, or loading plans."
    )
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', default=lambda self: self.env.ref('uom.product_uom_unit'),
        help="Unit of measure for this cargo commodity, used when the cargo commodities are not grouped in a package.")

    weight = fields.Float(
        string='Weight (total units)',
        help="Total weight of all units in this cargo commodity line. For example, if this line represents 300 units, "
            "this value should reflect the combined weight of those 300 units.")
    volume = fields.Float(
        string='Volume (total units)',
        help="Total volume of all units in this cargo commodity line. For example, if this line represents 300 units, "
            "this value should reflect the combined volume of those 300 units.")
    quantity = fields.Integer(
        string='Quantity',
        help="Number of units or packages of this cargo commodity. This is used to calculate the total weight and "
            "volume for the entire cargo template.")

    cargo_type_id = fields.Many2one('cargo.type', string='Cargo Type')
    hs_code_id = fields.Many2one('hs.code', string='HS Code')
    country_of_origin_id = fields.Many2one('res.country', string='Country of Origin (C/O)')
    import_tax_rate = fields.Float(
        string='Import Tax Rate',
        help="Import tax rate (in percentage) used to estimate import duties when handling inbound shipments. "
            "This field is primarily used in scenarios where the Forwarder provides customs declaration services "
            "or pays import taxes on behalf of the customer. When assigning an HS Code to a cargo, this rate "
            "can be referenced to calculate estimated import-related costs during quotation or shipment planning")

    is_danger = fields.Boolean(string='Is Dangerous Goods', help="Tick if this cargo commodity is a dangerous good.")
    dg_class_id = fields.Many2one('freight.dg.class', string='DG Class', help="Dangerous Goods (DG) Class applicable to this cargo commodity, if any.")
    un_number_id = fields.Many2one('freight.un.number', string='UN Number', help="United Nations Number associated with the dangerous goods.")
    packaging_group = fields.Selection(related='un_number_id.packaging_group', string='Packaging Group')
    flash_point = fields.Float(related='un_number_id.flash_point', string='Flash Point')

    # Marking and Notes
    need_marking = fields.Boolean(string='Need Marking')
    handling_instructions = fields.Text(string='Handling Instructions')

    # References
    cargo_template_data_id = fields.Many2one('freight.cargo.template.data', string='Cargo Template Data')

    @api.constrains('volume', 'weight', 'quantity')
    def _check_valid_dimensions_and_quantity(self):
        for record in self:
            if record.volume < 0:
                raise ValidationError(_("Volume of Cargo Commodity %s cannot be negative") % record.name)
            if record.weight < 0:
                raise ValidationError(_("Weight of Cargo Commodity %s cannot be negative") % record.name)
            if record.quantity < 0:
                raise ValidationError(_("Quantity of Cargo Commodity %s cannot be negative") % record.name)

    @api.depends('cargo_template_data_id.volume_uom_name')
    def _compute_volume_uom_name(self):
        for record in self:
            record.volume_uom_name = record.cargo_template_data_id.volume_uom_name

    @api.depends('cargo_template_data_id.weight_uom_name')
    def _compute_weight_uom_name(self):
        for record in self:
            record.weight_uom_name = record.cargo_template_data_id.weight_uom_name
