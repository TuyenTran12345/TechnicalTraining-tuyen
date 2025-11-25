from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CargoTemplateData(models.Model):
    _name = 'freight.cargo.template.data'
    _description = 'Freight Cargo Template Data'

    # General Information
    name = fields.Char(string='Name', required=True, help="Internal reference name for this cargo template.")

    # Packaging Information
    packing_mode = fields.Selection([
        ('package', 'Package'),
        ('bulk', 'Bulk Cargo'),
    ], string='Packing Mode', default='package', required=True,
        help="""Default packing mode used when generating packages for this cargo template.
        - Package: Cargo will be generated in packages eg: container, pallet, box...
        - Bulk Cargo: Use for cargo that cannot be packaged eg: cargo that is too large, too heavy, etc.
        """)
    package_type_id = fields.Many2one(
        'stock.package.type', string='Packaging Type',
        help="Default packaging type used when generating packages for this cargo template.")

    # Cargo Information for Bulk Cargo
    cargo_type_id = fields.Many2one('cargo.type', string='Cargo Type')
    hs_code_id = fields.Many2one('hs.code', string='HS Code')
    country_of_origin_id = fields.Many2one(
        'res.country',
        string='Country of Origin (C/O)',
        help="Country where the goods are produced or exported from. This information is used to determine "
            "the applicable import duties based on trade agreements and certificate of origin (C/O)."
    )
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
    need_marking = fields.Boolean(string='Need Marking')
    handling_instructions = fields.Text(string='Handling Instructions')

    # Dimensions
    weight = fields.Float(string='Net Weight', help="Net weight of each unit in this cargo template.")
    volume = fields.Float(string='Volume', help="Volume of each unit in this cargo template.")
    total_volume = fields.Float(
        string='Total Volume', compute='_compute_total_volume',
        help="Total volume of all units in this cargo template.")
    total_weight = fields.Float(
        string='Total Weight', compute='_compute_total_weight',
        help="Total weight of all units in this cargo template.")
    volume_uom_name = fields.Char(string='Volume Unit of Measure', compute='_compute_volume_uom_name')
    weight_uom_name = fields.Char(string='Weight Unit of Measure', compute='_compute_weight_uom_name')

    # References
    cargo_template_data_line_ids = fields.One2many('freight.cargo.template.data.line', 'cargo_template_data_id', string='Cargo Template Data Lines')

    @api.constrains('volume', 'weight')
    def _check_valid_dimensions(self):
        for record in self:
            if record.volume < 0:
                raise ValidationError(_("Volume of Cargo Template %s cannot be negative") % record.name)
            if record.weight < 0:
                raise ValidationError(_("Weight of Cargo Template %s cannot be negative") % record.name)

    # ================================================
    # ================Compute methods=================
    # ================================================
    def _compute_volume_uom_name(self):
        for record in self:
            record.volume_uom_name = self.env['product.template']._get_volume_uom_name_from_ir_config_parameter()

    def _compute_weight_uom_name(self):
        for record in self:
            record.weight_uom_name = self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    @api.onchange('package_type_id', 'packing_mode')
    def _onchange_package_type_id(self):
        if self.packing_mode == 'package' and self.package_type_id:
            self.volume = self.package_type_id.volume
            self.name = self.package_type_id.name
        elif self.packing_mode == 'bulk':
            self.name = _("Bulk Cargo")

    @api.depends('volume', 'packing_mode', 'cargo_template_data_line_ids.volume')
    def _compute_total_volume(self):
        for record in self:
            if record.packing_mode == 'package' and record.package_type_id:
                record.total_volume = record.package_type_id.volume
            else:  # bulk
                record.total_volume = record.volume

    @api.depends('weight', 'packing_mode', 'cargo_template_data_line_ids.weight')
    def _compute_total_weight(self):
        for record in self:
            if record.packing_mode == 'package':
                record.total_weight = sum(record.cargo_template_data_line_ids.mapped('weight'))
            else:  # bulk
                record.total_weight = record.weight
