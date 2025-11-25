from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(selection_add=[
        ('freight', 'Freight'),
        ('local_charge', 'Local Charge'),
    ], ondelete={'freight': 'set service', 'local_charge': 'set service'})
    support_freight_name = fields.Selection([
        ('manual', 'Manual Name'),
        ('auto', 'Auto Generate'),
    ], string='Naming Strategy', default='manual', required=True,
        help="Choose how freight service names are managed:\n"
        "- Manual Name: User sets the name manually\n"
        "- Auto Generate: System generates name from transport mode, shipping method and route")

    route_id = fields.Many2one(
        'route.route', string='Route',
        help="Predefined route associated with this freight service (e.g., Hai Phong -> Singapore).")
    port_id = fields.Many2one(
        'res.partner', string='Port', domain=[('is_port', '=', True)],
        help="Predefined port associated with this local charge service")
    transport_mode = fields.Selection([
        ('sea', 'Sea'),
        ('air', 'Air'),
        ('land', 'Land'),
    ], string='Transport Mode',
        help="Primary transport mode for the freight service (Sea, Air, or Land).")
    ocean_shipping_method_id = fields.Many2one(
        'freight.shipping.method', string='Ocean Shipping Method', domain=[('is_sea', '=', True)],
        help="Specific shipping method used if the transport mode is Sea (e.g., FCL, LCL, Bulk Cargo).")
    air_shipping_method_id = fields.Many2one(
        'freight.shipping.method', string='Air Shipping Method', domain=[('is_air', '=', True)],
        help="Specific shipping method used if the transport mode is Air (e.g., Express, Economy, Priority).")
    land_shipping_method_id = fields.Many2one(
        'freight.shipping.method', string='Land Shipping Method', domain=[('is_land', '=', True)],
        help="Specific shipping method used if the transport mode is Land (e.g., FTL, LTL, Project Cargo).")

    # --- Constraints ---
    @api.constrains('detailed_type', 'route_id', 'port_id')
    def _check_freight_product_constraints(self):
        for record in self:
            if record.detailed_type == 'freight' and not record.route_id:
                raise ValidationError(_("Route is required for freight products."))
            if record.detailed_type == 'local_charge' and not record.port_id:
                raise ValidationError(_("Port is required for local charge products."))

    # --- Override methods ---
    def _detailed_type_mapping(self):
        type_mapping = super()._detailed_type_mapping()
        type_mapping['freight'] = 'service'
        type_mapping['local_charge'] = 'service'
        return type_mapping

    # --- Onchange methods ---
    @api.onchange('detailed_type')
    def _onchange_freight_detailed_type(self):
        """
        Set default naming strategy when switching into/out of 'freight'.
        Clean up freight fields when leaving 'freight'.
        """
        if self.detailed_type != 'freight':
            self.route_id = False
            self.transport_mode = False
            self.ocean_shipping_method_id = False
            self.air_shipping_method_id = False
            self.land_shipping_method_id = False
            self.support_freight_name = 'manual'
        else:
            # Only set auto if context suggests it (e.g., from freight menu)
            # or if field is empty/False
            if (not self.support_freight_name or
                    self.env.context.get('default_support_freight_name') == 'auto'):
                self.support_freight_name = 'auto'
            self._onchange_autoname_preview()

    @api.onchange(
        'route_id', 'support_freight_name', 'transport_mode', 'detailed_type',
        'ocean_shipping_method_id', 'air_shipping_method_id', 'land_shipping_method_id'
    )
    def _onchange_autoname_preview(self):
        """
        Live preview the name while editing, if auto-name is enabled and type is 'freight'.
        """
        if self._should_auto_generate_name():
            self.name = self._generate_freight_name()

    @api.onchange('name')
    def _onchange_user_typed_name(self):
        """
        If user manually changes the name (and it's different from auto rule),
        switch to manual naming to respect user input.
        """
        for rec in self:
            if rec._should_auto_generate_name() and rec.name:
                expected_name = rec._generate_freight_name()
                # If user deviates from the rule, we respect manual input
                if rec.name.strip() != (expected_name or '').strip():
                    rec.support_freight_name = 'manual'

    # --- CRUD methods ---
    @api.model_create_multi
    def create(self, vals_list):
        """
        Generate freight name when auto-generation is enabled.
        Respects field default for support_freight_name (manual).
        """
        for vals in vals_list:
            if vals.get('detailed_type') == 'freight' and vals.get('support_freight_name') == 'auto':
                vals['name'] = self._generate_freight_name_from_vals(vals)
            if vals.get('detailed_type') == 'local_charge' and vals.get('port_id'):
                vals['name'] = self._generate_local_charge_name_from_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        """
        Handle freight name auto-generation during write operations.
        Respects manual naming when user directly edits the name field.
        """
        if self._should_disable_auto_naming(vals):
            self._disable_auto_naming_for_manual_edits()

        res = super().write(vals)

        # Auto-generate names when relevant fields change
        if self._should_regenerate_names(vals):
            self._regenerate_freight_names()

        return res

    # --- Helper methods ---
    def _get_freight_related_fields(self):
        """Return set of fields that affect freight name generation."""
        return {
            'transport_mode', 'ocean_shipping_method_id', 'air_shipping_method_id',
            'land_shipping_method_id', 'route_id', 'detailed_type', 'support_freight_name'
        }

    def _should_disable_auto_naming(self, vals):
        """Check if auto-naming should be disabled due to manual name edit."""
        return (
            'name' in vals
            and not self.env.context.get('force_autoname')
            and not self.env.context.get('skip_autoname')
        )

    def _disable_auto_naming_for_manual_edits(self):
        """Switch to manual naming for records with manual name edits."""
        manual_edit_records = self.filtered(
            lambda r: r.detailed_type == 'freight' and r.support_freight_name == 'auto'
        )
        if manual_edit_records:
            manual_edit_records.with_context(skip_autoname=True).write({
                'support_freight_name': 'manual'
            })

    def _should_regenerate_names(self, vals):
        """Check if names should be regenerated based on changed fields."""
        return (
            not self.env.context.get('skip_autoname')
            and bool(self._get_freight_related_fields() & set(vals))
        )

    def _regenerate_freight_names(self):
        """Regenerate names for applicable freight records."""
        for record in self.filtered(lambda r: r._should_auto_generate_name()):
            new_name = record._generate_freight_name()
            if new_name and new_name != record.name:
                record.with_context(skip_autoname=True).write(
                    {'name': new_name})

    def _should_auto_generate_name(self):
        """Check if auto-name generation should apply to this record."""
        self.ensure_one()
        return self.detailed_type == 'freight' and self.support_freight_name == 'auto'

    def _generate_freight_name(self):
        """
        Generate freight name from current record state.
        Used for onchange and write operations.
        """
        self.ensure_one()
        return self._build_freight_name(
            transport_mode=self.transport_mode,
            shipping_method=self._get_active_shipping_method(),
            route_name=self.route_id.name if self.route_id else None
        )

    def _generate_local_charge_name_from_vals(self, vals):
        """
        Generate local charge name from vals dictionary.
        Used during record creation.
        """
        port_id = vals.get('port_id')
        port = self.env['res.partner'].browse(port_id)
        port_name = f'{port.ref} ({port.country_id.code})'
        return f'{vals.get("name")} - {port_name}'

    @api.model
    def _generate_freight_name_from_vals(self, vals):
        """
        Generate freight name from vals dictionary.
        Used during record creation.
        """
        shipping_method = self._get_shipping_method_from_vals(vals)
        return self._build_freight_name(
            transport_mode=vals.get('transport_mode'),
            shipping_method=shipping_method,
            route_name=self._get_route_name_from_vals(vals)
        )

    def _build_freight_name(self, transport_mode=None, shipping_method=None, route_name=None):
        """
        Core method to build freight name from components.
        Centralizes name generation logic to eliminate duplication.

        Examples:
            _build_freight_name('sea', 'FCL', 'Hai Phong - Singapore')
            → "[Sea] FCL - Hai Phong - Singapore"

            _build_freight_name('air', 'Express', 'Hanoi - Los Angeles')
            → "[Air] Express - Hanoi - Los Angeles"
        """
        name_parts = []

        # Add transport mode in brackets
        if transport_mode:
            name_parts.append(f"[{transport_mode.capitalize()}]")

        if shipping_method:
            name_parts.append(shipping_method.name if hasattr(
                shipping_method, 'name') else str(shipping_method))

        if route_name:
            separator = "- " if name_parts else ""
            name_parts.append(f"{separator}{route_name}")

        return " ".join(name_parts) if name_parts else _("Freight")

    def _get_active_shipping_method(self):
        """Get the appropriate shipping method based on transport mode."""
        self.ensure_one()

        mode_method_map = {
            'sea': self.ocean_shipping_method_id,
            'air': self.air_shipping_method_id,
            'land': self.land_shipping_method_id,
        }

        if self.transport_mode and mode_method_map.get(self.transport_mode):
            return mode_method_map[self.transport_mode]

        return (self.ocean_shipping_method_id or
                self.air_shipping_method_id or
                self.land_shipping_method_id)

    def _get_shipping_method_from_vals(self, vals):
        """Extract shipping method from vals during creation."""
        method_id = (vals.get('ocean_shipping_method_id') or
            vals.get('air_shipping_method_id') or
            vals.get('land_shipping_method_id'))

        if method_id:
            method = self.env['freight.shipping.method'].browse(method_id)
            return method if method.exists() else None
        return None

    def _get_route_name_from_vals(self, vals):
        """Extract route name from vals during creation."""
        route_id = vals.get('route_id')
        if route_id:
            route = self.env['route.route'].browse(route_id)
            return route.name if route.exists() else None
        return None

    def _compute_display_name(self):
        super()._compute_display_name()
        for rec in self:
            if not rec.port_id:
                continue
            port_ref = rec.port_id.ref or ''
            country_code = rec.port_id.country_id.code or ''
            port_info = f'{port_ref} ({country_code})'
            base_name = rec.name or ''
            if port_info in base_name:
                rec.display_name = base_name
            else:
                rec.display_name = '%s - %s (%s)' % (base_name, port_ref, country_code)
