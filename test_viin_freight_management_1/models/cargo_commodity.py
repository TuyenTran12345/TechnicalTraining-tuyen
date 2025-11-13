from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CargoCommodity(models.Model):
    _name = 'cargo.commodity'
    _description = 'Cargo Commodity'

    name = fields.Char(
        string='Description', required=True, default=lambda self: _('New'),
        help="Short description or label for the commodity. Often auto-generated "
            "but can be manually updated to reflect the actual goods (e.g., 'TV 55 inch - Box 1').")

    volume_uom_name = fields.Char(string='Volume Unit of Measure', compute='_compute_volume_uom_name')
    weight_uom_name = fields.Char(string='Weight Unit of Measure', compute='_compute_weight_uom_name')

    is_individual_package = fields.Boolean(
        string='Is Individual Package',
        help="Tick if this commodity is a physical package that should be tracked separately (e.g., seal, weight, etc.)"
    )
    package_type_id = fields.Many2one(
        'stock.package.type', string='Package Type',
        help="Type of packaging used for this commodity (e.g., Carton, Pallet, Wooden Crate). "
            "Useful for volume estimation, or loading plans."
    )
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', default=lambda self: self.env.ref('uom.product_uom_unit'),
        help="Unit of measure for this commodity, used when the commodities are not grouped in a package.")

    weight = fields.Float(
        string='Weight (total units)',
        help="Total weight of all units in this commodity line. For example, if this line represents 300 units, "
            "this value should reflect the combined weight of those 300 units.")
    volume = fields.Float(
        string='Volume (total units)',
        help="Total volume of all units in this commodity line. For example, if this line represents 300 units, "
            "this value should reflect the combined volume of those 300 units.")
    quantity = fields.Integer(
        string='Quantity',
        help="Number of units or packages of this commodity. This is used to calculate the total weight and volume for the entire cargo template.")

    cargo_type_id = fields.Many2one('cargo.type', string='Cargo Type')
    hs_code_id = fields.Many2one('hs.code', string='HS Code')
    country_of_origin_id = fields.Many2one('res.country', string='Country of Origin (C/O)')
    import_tax_rate = fields.Float(string='Import Tax Rate')

    is_danger = fields.Boolean(string='Is Dangerous Goods', help="Tick if this item is a dangerous good.")
    dg_class_id = fields.Many2one('freight.dg.class', string='DG Class', help="Dangerous Goods (DG) Class applicable to this item, if any.")
    un_number_id = fields.Many2one('freight.un.number', string='UN Number', help="United Nations Number associated with the dangerous goods.")
    packaging_group = fields.Selection(related='un_number_id.packaging_group', string='Packaging Group')
    flash_point = fields.Float(related='un_number_id.flash_point', string='Flash Point')

    # Marking and Notes
    need_marking = fields.Boolean(string='Need Marking')
    shipping_mark = fields.Char(string='Shipping Mark')
    handling_instructions = fields.Text(string='Handling Instructions')

    # References
    package_ids = fields.Many2many('freight.package', 'cargo_commodity_package_rel', 'cargo_commodity_id', 'package_id', string='Packages')
    cargo_template_id = fields.Many2one('cargo.template', string='Cargo Template')
    booking_ids = fields.Many2many('freight.booking', 'freight_booking_cargo_commodity_rel', 'cargo_commodity_id', 'booking_id', string='Bookings')
    shipment_id = fields.Many2one('freight.shipment', string='Shipment')
    route_ids = fields.Many2many(
        'freight.route', 'freight_route_cargo_commodity_rel', 'cargo_commodity_id', 'route_id',
        string='Routes',
    )

    booking_status = fields.Selection(selection=[
        ('not_ready', 'Not Ready'),
        ('need_booking', 'Need Booking'),
        ('booking_in_progress', 'Booking in Progress'),
        ('booked', 'Booked'),
    ], string='Booking Status', default='not_ready', compute='_compute_booking_status')
    main_route_id = fields.Many2one(
        'freight.route', string='Main Route', related='shipment_id.main_route_id', store=True
    )

    @api.constrains('volume', 'weight', 'quantity')
    def _check_valid_dimensions_and_quantity(self):
        for record in self:
            if record.volume < 0:
                raise ValidationError(_("Volume of Cargo Commodity %s cannot be negative") % record.name)
            if record.weight < 0:
                raise ValidationError(_("Weight of Cargo Commodity %s cannot be negative") % record.name)
            if record.quantity < 0:
                raise ValidationError(_("Quantity of Cargo Commodity %s cannot be negative") % record.name)

    @api.depends('shipment_id.volume_uom_name')
    def _compute_volume_uom_name(self):
        for record in self:
            record.volume_uom_name = record.shipment_id.volume_uom_name

    @api.depends('shipment_id.weight_uom_name')
    def _compute_weight_uom_name(self):
        for record in self:
            record.weight_uom_name = record.shipment_id.weight_uom_name

    @api.depends('booking_ids.state', 'route_ids.booking_ids', 'shipment_id.multiple_leg_route')
    def _compute_booking_status(self):
        for record in self:
            booking_status = 'not_ready'
            if not record.shipment_id.multiple_leg_route:
                if record.booking_ids:
                    if any(booking.state == 'draft' for booking in record.booking_ids):
                        booking_status = 'booking_in_progress'
                    elif all(booking.state in ('confirmed', 'done') for booking in record.booking_ids):
                        booking_status = 'booked'
                else:
                    booking_status = 'need_booking'
            else:
                if not record.route_ids:
                    booking_status = 'not_ready'
                else:
                    need_booking = False
                    for route in record.route_ids:
                        if not route.booking_ids:
                            need_booking = True
                            break
                        # In the case of adding a cargo to the package, and the old cargo list has already been booked, then a new booking is needed for the cargo
                        if route.booking_ids and any(booking_id not in record.booking_ids.ids for booking_id in route.booking_ids.ids):
                            need_booking = True
                            break
                    if need_booking:
                        booking_status = 'need_booking'
                    else:
                        booking_status = 'booked'
            record.booking_status = booking_status

    def convert_to_template(self):
        """In the case customer often ship the same kind of cargo, use this function in action server of bulk cargo commodity
        to create cargo template data, reuse and setup cargo information quickly in shipment.
        """
        cargo_template_data_vals_list = []
        cargo_template_datas = self.env['freight.cargo.template.data']
        for r in self:
            cargo_template_data_vals = {
                'name': f'{r.name} - {r.shipment_id.customer_id.name}' if r.shipment_id.customer_id else r.name,
                'packing_mode': 'bulk',
                'volume': r.volume,
                'weight': r.weight,
                'cargo_type_id': r.cargo_type_id.id,
                'hs_code_id': r.hs_code_id.id,
                'country_of_origin_id': r.country_of_origin_id.id,
                'is_danger': r.is_danger,
                'dg_class_id': r.dg_class_id.id,
                'un_number_id': r.un_number_id.id,
                'need_marking': r.need_marking,
                'handling_instructions': r.handling_instructions,
            }
            cargo_template_data_vals_list.append(cargo_template_data_vals)
        if cargo_template_data_vals_list:
            cargo_template_datas |= self.env['freight.cargo.template.data'].create(cargo_template_data_vals_list)
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_cargo_template_data')
        action['domain'] = [('id', 'in', cargo_template_datas.ids)]
        return action

    def _prepare_cargo_template_data_line_vals_list(self):
        """Prepare cargo template data line values list for create cargo template data line.
        This function is used to prepare data for create cargo template data line when convert 1 package to 1 cargo template,
        suitable for cargo that is packaged.
        """
        cargo_vals_list = []
        for cargo in self:
            cargo_vals_list.append({
                'name': cargo.name,
                'quantity': cargo.quantity,
                'weight': cargo.weight,
                'volume': cargo.volume,
                'is_individual_package': cargo.is_individual_package,
                'package_type_id': cargo.package_type_id.id,
                'uom_id': cargo.uom_id.id,
                'cargo_type_id': cargo.cargo_type_id.id,
                'hs_code_id': cargo.hs_code_id.id,
                'country_of_origin_id': cargo.country_of_origin_id.id,
                'is_danger': cargo.is_danger,
                'dg_class_id': cargo.dg_class_id.id,
                'un_number_id': cargo.un_number_id.id,
                'handling_instructions': cargo.handling_instructions,
                'need_marking': cargo.need_marking,
            })
        return cargo_vals_list

    def _prepare_booking_vals(self):
        """
        Prepare values for creating a booking from cargo commodity.
        Group cargo commodities by carrier to create optimal bookings, avoiding duplicate bookings
        for cargo commodities on multiple routes with the same carrier
        @return: list of booking values dictionaries
        """
        booking_vals_list = []

        group_cargo_commodity_by_carrier = defaultdict(
            lambda: self.env['cargo.commodity'])

        carrier_routes = defaultdict(set)

        for record in self:
            if record.booking_status == 'need_booking':
                for route in record.route_ids or record.main_route_id:
                    group_cargo_commodity_by_carrier[route.carrier_id] |= record
                    carrier_routes[route.carrier_id].add(route.id)

        for carrier, cargo_commodities in group_cargo_commodity_by_carrier.items():
            if cargo_commodities:
                route_ids = list(carrier_routes[carrier])
                shipment = cargo_commodities[0].shipment_id
                booking_vals = {
                    'shipment_id': shipment.id,
                    'multiple_leg_route': len(route_ids) > 1,
                    'cargo_commodity_ids': [(6, 0, cargo_commodities.ids)],
                    'carrier_id': carrier.id,
                    'freight_route_ids': [(6, 0, route_ids)],
                    'shipper_id': shipment.shipper_id.id,
                    'consignee_id': shipment.consignee_id.id,
                    'notify_party_id': shipment.notify_party_id.id,
                    'master_bill_number': shipment.master_bill_number,
                }

                if len(route_ids) == 1:
                    route = self.env['freight.route'].browse(route_ids[0])
                    booking_vals.update({
                        'route_id': route.route_id.id,
                        'service_type': route.service_type,
                        'transport_mode': route.transport_mode,
                        'ocean_shipping_method_id': route.ocean_shipping_method_id.id,
                        'air_shipping_method_id': route.air_shipping_method_id.id,
                        'land_shipping_method_id': route.land_shipping_method_id.id,
                        'etd': route.etd,
                        'eta': route.eta,
                        'cutoff': route.cutoff,
                        'origin_id': route.origin_id.id,
                        'destination_id': route.destination_id.id,
                    })

                    port_vals = route._get_port_vals_by_service_type()
                    if port_vals:
                        booking_vals.update(port_vals)

                booking_vals_list.append(booking_vals)

        return booking_vals_list

    def write(self, vals):
        if self.booking_status == 'booked':
            raise ValidationError(_(
                "You cannot change a booked cargo commodity %s. "
                "If you want to change it, please set status of all booking for this cargo commodity to Draft before changing."
            ) % self.name)
        return super(CargoCommodity, self).write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_booked_cargo_commodity(self):
        for record in self:
            if record.booking_status == 'booked':
                raise ValidationError(_(
                    "You cannot delete a booked cargo commodity %s. "
                    "If you want to delete it, please set status of all booking for this cargo commodity to Draft before deleting."
                ) % record.name)
