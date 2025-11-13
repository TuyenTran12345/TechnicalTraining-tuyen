from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CargoTemplate(models.Model):
    _name = 'cargo.template'
    _description = 'Cargo Template'

    # General Information
    name = fields.Char(string='Name', required=True, help="Internal reference name for the cargo template.")
    cargo_template_data_id = fields.Many2one(
        'freight.cargo.template.data', string='Template Data', required=True,
        help="Choose template data to create cargo template for this shipment.")
    quantity = fields.Integer(
        string='Quantity', default=1,
        help="Number of packages or cargo commodities to be created for this cargo template.")

    # References
    shipment_id = fields.Many2one('freight.shipment', string='Shipment')
    cargo_commodity_ids = fields.One2many('cargo.commodity', 'cargo_template_id', string='Cargo Details')
    package_ids = fields.One2many('freight.package', 'cargo_template_id', string='Packages')

    # technical fields
    is_generated = fields.Boolean(
        string='Is Generated',
        compute='_compute_is_generated',
        help="Technical field indicating whether all cargo commodities/packages required have been generated.")

    @api.constrains('quantity')
    def _check_valid_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError(_("Quantity of Cargo Template %s cannot be negative") % record.name)

    # ================================================
    # ================Compute methods=================
    # ================================================

    @api.depends('cargo_template_data_id.packing_mode', 'package_ids', 'cargo_commodity_ids')
    def _compute_is_generated(self):
        for record in self:
            package_mode = record.cargo_template_data_id.packing_mode
            if package_mode == 'package':
                record.is_generated = len(record.package_ids) >= record.quantity
            elif package_mode == 'bulk':
                record.is_generated = len(record.cargo_commodity_ids) >= record.quantity
            else:
                record.is_generated = False

    @api.onchange('cargo_template_data_id')
    def _onchange_cargo_template_data_id(self):
        if self.cargo_template_data_id:
            self.name = self.cargo_template_data_id.name

    # ================================================
    # ================Business methods================
    # ================================================
    def _generator_to_cargo_details(self):
        """
        Automatically generate cargo details (bulk cargo or packages) from unprocessed cargo templates linked to this shipment.

        This method is used to quickly create cargo details (shipments or packages) from unprocessed cargo templates
        linked to this shipment. Without this automation, users would need to manually create each freight shipment or
        package one by one based on the cargo template information, which is tedious and error-prone.

        Typically, this action is triggered by logistics coordinators or warehouse operators after confirming
        the cargo templates but before finalizing booking and shipment arrangements.
        """
        package_vals_list = []
        cargo_commodity_vals_list = []
        for record in self.filtered(lambda r: not r.is_generated):
            package_mode = record.cargo_template_data_id.packing_mode
            if package_mode == 'package':
                package_vals_list.extend(record._prepare_package_vals())
            elif package_mode == 'bulk':
                cargo_commodity_vals_list.extend(record._prepare_cargo_vals())
        if package_vals_list:
            self.env['freight.package'].create(package_vals_list)
        if cargo_commodity_vals_list:
            self.env['cargo.commodity'].create(cargo_commodity_vals_list)

    def _prepare_package_vals(self):
        """Prepare package values list for create packaging list.
        """
        self.ensure_one()
        package_vals_list = []
        cargo_template_data = self.cargo_template_data_id
        for i in range(self.quantity - len(self.package_ids)):
            name = self.name + ' - ' + str(i + 1)
            package_type_id = cargo_template_data.package_type_id.id
            package_vals = {
                'name': name,
                'cargo_template_id': self.id,
                'shipment_id': self.shipment_id.id,
                'package_type_id': package_type_id,
                'weight': cargo_template_data.weight,
                'volume': cargo_template_data.volume
            }
            if cargo_template_data.cargo_template_data_line_ids:
                cargo_commodity_vals_list = self._prepare_cargo_vals_from_template()
                package_vals['cargo_commodity_ids'] = [(0, 0, cargo_commodity_vals) for cargo_commodity_vals in cargo_commodity_vals_list]
            package_vals_list.append(package_vals)
        return package_vals_list

    def _prepare_cargo_vals(self):
        """Prepare cargo values list for create bulk cargo.
        """
        self.ensure_one()
        cargo_vals_list = []
        cargo_template_data = self.cargo_template_data_id
        for i in range(self.quantity - len(self.cargo_commodity_ids)):
            name = self.name + ' - ' + str(i + 1)
            cargo_vals_list.append({
                'name': name,
                'cargo_template_id': self.id,
                'shipment_id': self.shipment_id.id,
                'weight': cargo_template_data.total_weight / self.quantity,
                'volume': cargo_template_data.total_volume / self.quantity,
                'quantity': 1,
                'cargo_type_id': cargo_template_data.cargo_type_id.id,
                'hs_code_id': cargo_template_data.hs_code_id.id,
                'country_of_origin_id': cargo_template_data.country_of_origin_id.id,
                'is_danger': cargo_template_data.is_danger,
                'dg_class_id': cargo_template_data.dg_class_id.id,
                'un_number_id': cargo_template_data.un_number_id.id,
                'packaging_group': cargo_template_data.packaging_group,
                'flash_point': cargo_template_data.flash_point,
                'need_marking': cargo_template_data.need_marking,
                'handling_instructions': cargo_template_data.handling_instructions,
            })
        return cargo_vals_list

    def _prepare_cargo_vals_from_template(self):
        """Prepare cargo values list for cargo commodity on packages
        """
        self.ensure_one()
        cargo_vals_list = []
        for line in self.cargo_template_data_id.cargo_template_data_line_ids:
            cargo_vals_list.append({
                'name': line.name,
                'cargo_template_id': self.id,
                'shipment_id': self.shipment_id.id,
                'quantity': line.quantity,
                'weight': line.weight,
                'volume': line.volume,
                'cargo_type_id': line.cargo_type_id.id,
                'hs_code_id': line.hs_code_id.id,
                'country_of_origin_id': line.country_of_origin_id.id,
                'is_danger': line.is_danger,
                'dg_class_id': line.dg_class_id.id,
                'un_number_id': line.un_number_id.id,
                'need_marking': line.need_marking,
                'handling_instructions': line.handling_instructions,
                'is_individual_package': line.is_individual_package,
                'package_type_id': line.package_type_id.id,
                'uom_id': line.uom_id.id,
            })
        return cargo_vals_list
