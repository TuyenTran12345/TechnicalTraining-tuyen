from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightPackage(models.Model):
    _name = 'freight.package'
    _description = 'Shipping Container & Package'

    name = fields.Char(
        string='Description', required=True,
        default=lambda self: _('New'),
        help="Internal reference name for the package."
    )
    package_type_id = fields.Many2one(
        'stock.package.type', string='Package Type', required=True,
        help="Specify the type of packaging used (e.g., pallet, container, drum)."
    )
    is_container = fields.Boolean(string='Is Container', related='package_type_id.is_container', store=True)
    quantity = fields.Integer(
        string='Number of Cargos',
        compute='_compute_quantity',
        help="Sum of Cargos quantity in this package, will be calculated from the list of cargos."
    )

    volume_uom_name = fields.Char(string='Volume Unit of Measure', compute='_compute_volume_uom_name')
    weight_uom_name = fields.Char(string='Weight Unit of Measure', compute='_compute_weight_uom_name')

    weight = fields.Float(
        string='Weight',
        compute='_compute_weight',
        store=True,
        readonly=False,
        help="Total weight of all cargo commodities in the package, automatically calculated."
    )
    volume = fields.Float(string='Volume', compute='_compute_volume', store=True, readonly=False)

    seal_number = fields.Char(
        string='Seal Number',
        help="Seal number affixed to the container to ensure cargo security and integrity. "
            "Mandatory for FCL shipments. Must match the seal recorded on the Bill of Lading and shipping documents."
    )

    container_number = fields.Char(
        string='Container Number',
        help="Unique identifier for the shipping container (e.g., MSCU1234567). "
            "Required for all FCL and LCL shipments. Used for manifest declarations, tracking, and cargo release."
    )

    shipping_mark = fields.Char(
        string='Shipping Mark',
        help="Identification marks printed or attached to the package. "
            "Typically includes consignee name, destination, order reference, and handling instructions "
            "(e.g., 'ABC Corp - Tokyo - PO#5678 - 1/10'). "
            "Essential for managing multiple packages and ensuring correct delivery."
    )

    handling_instructions = fields.Text(
        string='Handling Instructions',
        help="Enter any special handling instructions for the package, such as "
            "'Fragile', 'Keep Upright', 'Do Not Stack', or temperature requirements. "
            "Important for ensuring safe transport and delivery."
    )

    cargo_mode = fields.Selection(related='shipment_id.cargo_mode')
    cargo_commodity_ids = fields.Many2many(
        'cargo.commodity', 'cargo_commodity_package_rel',
        'package_id', 'cargo_commodity_id', string='Cargo Details'
    )
    cargo_note_details = fields.Text(string='Cargo Note Details', help="Free-form text to summarize cargo details.")

    # References
    cargo_template_id = fields.Many2one('cargo.template', string='Cargo Template')
    booking_ids = fields.Many2many('freight.booking', 'freight_booking_package_rel', 'package_id', 'booking_id', string='Bookings')
    shipment_id = fields.Many2one('freight.shipment', string='Shipment')
    route_ids = fields.Many2many(
        'freight.route', 'freight_route_package_rel', 'package_id', 'route_id', string='Routes'
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

    # ================================================
    # ================Constraints=====================
    # ================================================

    @api.constrains('weight', 'volume')
    def _check_valid_dimensions(self):
        for record in self:
            if record.weight < 0:
                raise ValidationError(_("Weight of Package %s cannot be negative") % record.name)
            if record.volume < 0:
                raise ValidationError(_("Volume of Package %s cannot be negative") % record.name)

    # ================================================
    # ================Compute methods=================
    # ================================================

    @api.depends('shipment_id.volume_uom_name')
    def _compute_volume_uom_name(self):
        for record in self:
            record.volume_uom_name = record.shipment_id.volume_uom_name

    @api.depends('shipment_id.weight_uom_name')
    def _compute_weight_uom_name(self):
        for record in self:
            record.weight_uom_name = record.shipment_id.weight_uom_name

    @api.depends('cargo_commodity_ids.weight')
    def _compute_weight(self):
        for record in self:
            record.weight = sum(record.cargo_commodity_ids.mapped('weight'))

    @api.depends('package_type_id.volume')
    def _compute_volume(self):
        for record in self:
            record.volume = record.package_type_id.volume

    @api.depends('cargo_commodity_ids.quantity')
    def _compute_quantity(self):
        for record in self:
            record.quantity = sum(record.cargo_commodity_ids.mapped('quantity'))

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

    # ================================================
    # ================Business Methods================
    # ================================================

    def action_add_cargo_commodity(self):
        self.ensure_one()
        return {
            'name': _('Add Cargo'),
            'type': 'ir.actions.act_window',
            'res_model': 'cargo.commodity',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_shipment_id': self.shipment_id.id,
                'default_package_ids': [(4, self.id)],
            }
        }

    def action_view_cargo_commodities(self):
        self.ensure_one()
        return {
            'name': _('Cargo Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'cargo.commodity',
            'view_mode': 'tree,form',
            'domain': [('package_ids', 'in', self.ids)],
            'context': {
                'default_shipment_id': self.shipment_id.id,
                'default_package_ids': [(4, self[:1].id)],
            }
        }

    def convert_to_template(self):
        """In the case customer often ship the same kind of cargo, use this function in action server of package
        to create cargo template data, reuse and setup cargo information quickly in shipment.
        """
        cargo_template_data_vals_list = []
        cargo_template_datas = self.env['freight.cargo.template.data']
        for r in self:
            cargo_template_data_vals = {
                'name': f'{r.name} - {r.shipment_id.customer_id.name}' if r.shipment_id.customer_id else r.name,
                'packing_mode': 'package',
                'package_type_id': r.package_type_id.id,
                'cargo_type_id': r.cargo_commodity_ids.cargo_type_id.id,
                'volume': r.volume,
            }
            if r.cargo_commodity_ids:
                cargo_template_data_vals['cargo_template_data_line_ids'] = [
                    (0, 0, vals) for vals in r.cargo_commodity_ids._prepare_cargo_template_data_line_vals_list()
                ]
            cargo_template_data_vals_list.append(cargo_template_data_vals)
        if cargo_template_data_vals_list:
            cargo_template_datas |= self.env['freight.cargo.template.data'].create(cargo_template_data_vals_list)
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_cargo_template_data')
        action['domain'] = [('id', 'in', cargo_template_datas.ids)]
        return action

    def _prepare_booking_vals(self):
        """
        Prepare values for creating a booking from package
        Group packages by carrier to create optimal bookings, avoiding duplicate bookings
        for packages on multiple routes with the same carrier
        @return: list of booking values dictionaries
        """
        booking_vals_list = []

        group_package_by_carrier = defaultdict(
            lambda: self.env['freight.package'])

        carrier_routes = defaultdict(set)

        for record in self:
            if record.booking_status == 'need_booking':
                for route in record.route_ids or record.main_route_id:
                    group_package_by_carrier[route.carrier_id] |= record
                    carrier_routes[route.carrier_id].add(route.id)

        for carrier, packages in group_package_by_carrier.items():
            if packages:
                route_ids = list(carrier_routes[carrier])
                shipment = packages[0].shipment_id
                booking_vals = {
                    'shipment_id': shipment.id,
                    'multiple_leg_route': len(route_ids) > 1,
                    'package_ids': [(6, 0, packages.ids)],
                    'carrier_id': carrier.id,
                    'freight_route_ids': [(6, 0, route_ids)],
                    'shipper_id': shipment.shipper_id.id,
                    'consignee_id': shipment.consignee_id.id,
                    'notify_party_id': shipment.notify_party_id.id,
                    'cargo_commodity_ids': [(6, 0, packages.cargo_commodity_ids.ids)],
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
                "You cannot change a booked package %s. "
                "If you want to change it, please set status of all booking for this package to Draft before changing."
            ) % self.name)
        return super(FreightPackage, self).write(vals)

    def unlink(self):
        cargo_commodity_ids = self.cargo_commodity_ids
        res = super(FreightPackage, self).unlink()
        cargo_commodity_ids.unlink()
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_except_booked_package(self):
        """Only unlink package that is not booked
        """
        for record in self:
            if record.booking_status == 'booked':
                raise ValidationError(_(
                    "You cannot delete a booked package %s. "
                    "If you want to delete it, please set status of all booking for this package to Draft before "
                    "deleting."
                ) % record.name)
