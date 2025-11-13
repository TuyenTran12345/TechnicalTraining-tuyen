from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightTransportMixin(models.AbstractModel):
    """Abstract model providing shared fields and methods for managing transport information
    across freight operations such as shipment, booking, route, and tracking.
    """

    _name = 'freight.transport.mixin'
    _description = 'Freight Transport Mixin'

    direction = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ('domestic', 'Domestic')
    ], string='Direction', required=True, default='export', tracking=True,
    help="Define the transport direction:\n"
        "- Import: Cargo moved from a foreign country into the domestic destination.\n"
        "- Export: Cargo shipped from the domestic origin to a foreign country.\n"
        "- Domestic: Cargo transported within the same country.")

    service_type = fields.Selection([
        ('door_to_door', 'Door to Door'),
        ('port_to_port', 'Port to Port'),
        ('port_to_door', 'Port to Door'),
        ('door_to_port', 'Door to Port')
    ], string='Service Type', required=True, default='door_to_door', tracking=True,
    help="Specify the scope of transport service:\n"
        "- Door to Door: Pickup from the shipper's location and delivery to the consignee's location.\n"
        "- Port to Port: Transport between the port of loading and the port of discharge only.\n"
        "- Port to Door: Pickup from the port of loading and delivery to the consignee's location.\n"
        "- Door to Port: Pickup from the shipper's location and delivery to the port of discharge.")

    # Related Partners
    customer_id = fields.Many2one(
        'res.partner', string='Customer',
        compute='_compute_customer_id', store=True, readonly=False,
        help="The directly customer requested transport this shipment, and its value is taken from the sales order.")
    consignee_id = fields.Many2one(
        'res.partner', string='Consignee', tracking=True,
        help="The consignee is the party that will receive the shipment.")
    shipper_id = fields.Many2one(
        'res.partner', string='Shipper', tracking=True,
        help="The shipper is the party that will send the shipment.")
    notify_party_id = fields.Many2one(
        'res.partner', string='Notify Party', tracking=True,
        help="The notify party is the party that will be notified when the shipment is ready for pickup or delivery.")
    agent_id = fields.Many2one(
        'res.partner', string='Agent', tracking=True,
        help="The agent is the party that will handle the shipment.")
    carrier_id = fields.Many2one(
        'res.partner', string='Carrier', tracking=True,
        help="The carrier is the party that will transport the shipment.")

    # Transport Info
    transport_mode = fields.Selection([
        ('sea', 'Sea Freight'),
        ('air', 'Air Freight'),
        ('land', 'Land Transport'),
        ('multiple', 'Multi-modal'),
    ], string='Transport Mode', tracking=True)

    ocean_shipping_method_id = fields.Many2one(
        'freight.shipping.method', string='Ocean Shipping Method',
        domain=[('is_sea', '=', True)], tracking=True
    )
    air_shipping_method_id = fields.Many2one(
        'freight.shipping.method', string='Air Shipping Method',
        domain=[('is_air', '=', True)], tracking=True
    )
    land_shipping_method_id = fields.Many2one(
        'freight.shipping.method', string='Truck Shipping Method',
        domain=[('is_land', '=', True)], tracking=True
    )

    vessel_name = fields.Char(string='Vessel Name', tracking=True)
    vessel_voyage_number = fields.Char(string='Vessel Voyage Number', tracking=True)
    air_name = fields.Char(string='Flight No.', tracking=True)
    air_voyage_number = fields.Char(string='Air Voyage Number', tracking=True)
    truck_name = fields.Char(string='Truck No.', tracking=True)
    driver_id = fields.Many2one('res.partner', string='Driver', tracking=True)

    # Schedule
    etd = fields.Datetime(
        string='ETD',
        tracking=True,
        help="Estimated Time of Departure. The planned date and time when the shipment or transport is expected to leave."
    )

    eta = fields.Datetime(
        string='ETA',
        tracking=True,
        help="Estimated Time of Arrival. The planned date and time when the shipment or transport is expected to arrive at the destination."
    )

    cutoff = fields.Datetime(
        string='Cutoff',
        tracking=True,
        help="Cut-off Time. The latest date and time by which the cargo or container must be delivered to the terminal/warehouse to ensure the shipment can be loaded and depart as scheduled."
    )

    atd = fields.Datetime(
        string='ATD',
        tracking=True,
        help="Actual Time of Departure. The real departure time of the shipment."
    )

    ata = fields.Datetime(
        string='ATA',
        tracking=True,
        help="Actual Time of Arrival. The real arrival time of the shipment."
    )

    # Route
    route_id = fields.Many2one(
        'route.route', string='Route', tracking=True,
        help="If you want fast setup origin and destination for this transport, "
        "you can select a route here. The system will get the origin and destination "
        "from the route to fill in the origin and destination fields."
    )
    origin_id = fields.Many2one('res.partner', string='Origin')
    port_of_loading_id = fields.Many2one('res.partner', string='Port of Loading')
    destination_id = fields.Many2one('res.partner', string='Destination')
    port_of_discharge_id = fields.Many2one('res.partner', string='Port of Discharge')

    volume_uom_name = fields.Char(string='Volume Unit of Measure', compute='_compute_volume_uom_name')
    weight_uom_name = fields.Char(string='Weight Unit of Measure', compute='_compute_weight_uom_name')

    total_packages = fields.Integer(
        string='Total Packages',
        compute='_compute_counts', compute_sudo=True,
        help="Total number of packages in the shipment"
    )
    total_cargo_commodities = fields.Integer(
        string='Total Cargo Commodities',
        compute='_compute_counts', store=True, readonly=False, compute_sudo=True,
        help="Total number of cargo commodities in the shipment"
    )
    total_weight = fields.Float(string='Total Weight', compute='_compute_cargo_totals', store=True, readonly=False)
    total_volume = fields.Float(string='Total Volume', compute='_compute_cargo_totals', store=True, readonly=False)

    # Related Sale Order Line
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm', related='sale_order_id.incoterm', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    description = fields.Text(string='Description')

    @api.constrains('etd', 'eta', 'atd', 'ata', 'cutoff')
    def _check_valid_timelines(self):
        for record in self:
            if record.etd and record.eta and record.etd > record.eta:
                raise ValidationError(_("ETD of Transport %s must be before ETA") % record.display_name)
            if record.atd and record.ata and record.atd > record.ata:
                raise ValidationError(_("ATD of Transport %s must be before ATA") % record.display_name)
            if record.cutoff and record.etd and record.cutoff > record.etd:
                raise ValidationError(_("Cutoff of Transport %s must be before ETD") % record.display_name)
            if record.cutoff and record.eta and record.cutoff > record.eta:
                raise ValidationError(_("Cutoff of Transport %s must be before ETA") % record.display_name)

    def _compute_volume_uom_name(self):
        product_length_in_feet_param = self.env['ir.config_parameter'].sudo().get_param('product.volume_in_cubic_feet')
        for record in self:
            if product_length_in_feet_param == '1':
                record.volume_uom_name = self.env.ref('viin_freight_management.product_uom_cbf').display_name
            else:
                record.volume_uom_name = self.env.ref('viin_freight_management.product_uom_cbm').display_name

    def _compute_weight_uom_name(self):
        for record in self:
            record.weight_uom_name = self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    def _compute_cargo_totals(self):
        for record in self:
            # This method should be overridden in models that inherit this mixin
            # to provide specific implementation based on their structure
            record.total_weight = 0
            record.total_volume = 0

    def _compute_counts(self):
        for record in self:
            # This method should be overridden in models that inherit this mixin
            # to provide specific implementation based on their structure
            record.total_packages = 0
            record.total_cargo_commodities = 0

    @api.depends('sale_order_id.partner_id')
    def _compute_customer_id(self):
        for record in self:
            if record.sale_order_id:
                record.customer_id = record.sale_order_id.partner_id

    @api.onchange('transport_mode')
    def _onchange_transport_mode(self):
        """Reset all fields that are not related to the transport mode"""
        if self.transport_mode == 'sea':
            self.air_shipping_method_id = False
            self.land_shipping_method_id = False
            self.air_name = False
            self.truck_name = False
        elif self.transport_mode == 'air':
            self.ocean_shipping_method_id = False
            self.land_shipping_method_id = False
            self.vessel_name = False
            self.truck_name = False
        elif self.transport_mode == 'land':
            self.ocean_shipping_method_id = False
            self.air_shipping_method_id = False
            self.vessel_name = False
            self.air_name = False

    @api.onchange('service_type', 'route_id')
    def _onchange_service_type(self):
        """Update origin, destination, and ports based on service type and route"""
        if not self.route_id:
            return
        start_point = self.route_id.departure_id
        end_point = self.route_id.destination_id

        self.origin_id = start_point
        self.destination_id = end_point

        self.port_of_loading_id = False
        self.port_of_discharge_id = False

        if self.service_type == 'port_to_port':
            self.port_of_loading_id = start_point
            self.port_of_discharge_id = end_point

        elif self.service_type == 'port_to_door':
            self.port_of_loading_id = start_point

        elif self.service_type == 'door_to_port':
            self.port_of_discharge_id = end_point

        elif self.service_type == 'door_to_door':
            pass

    def _get_core_transport_info_fields(self):
        """
        Core transport info fields used by multiple business logic such as
        updating main route and tracking booking change.
        """
        return [
            'transport_mode', 'service_type',
            'consignee_id', 'notify_party_id', 'carrier_id', 'agent_id',
            'ocean_shipping_method_id', 'vessel_name', 'vessel_voyage_number',
            'air_shipping_method_id', 'air_name', 'air_voyage_number',
            'land_shipping_method_id', 'driver_id', 'truck_name',
            'origin_id', 'port_of_loading_id', 'port_of_discharge_id', 'destination_id',
            'etd', 'atd', 'eta', 'ata', 'cutoff',
        ]

    def _get_booking_records(self):
        """
        Get the booking records for this transport.
        """
        return self.env['freight.booking']

    def _get_sensitive_fields_for_tracking_change_after_booking(self):
        """
        Returns fields that, when changed after booking is confirmed,
        should be logged on the related booking record.
        """
        return self._get_core_transport_info_fields()

    def _validating_tracking_model(self):
        """
        Validating the tracking model.
        """
        return self._name in ['freight.shipment', 'freight.route']

    def _log_sensitive_changes_to_booking(self, changed_fields, old_values):
        """
        Log changes to sensitive fields for confirmed bookings.

        :param changed_fields: List/set of fields that were attempted to update
        :param old_values: Dict[record.id][field] = old_value, captured before write
        """
        for record in self:
            confirmed_bookings = record._get_booking_records().filtered(
                lambda b: b.state in ['confirmed', 'done'])
            if not confirmed_bookings:
                continue

            changes = []
            for field in changed_fields:
                old = old_values.get(record.id, {}).get(field)
                new = record[field]

                if record._fields[field].type == 'many2one':
                    old_id = old.id if hasattr(old, 'id') else old
                    new_id = new.id if hasattr(new, 'id') else False
                    if old_id == new_id:
                        continue
                else:
                    if old == new:
                        continue

                field_label = record._fields[field].string
                if record._fields[field].type == 'many2one':
                    old_display = self.env['res.partner'].browse(old).display_name if old else '⌀'
                    new_display = new.display_name if hasattr(new, 'display_name') else '⌀'
                else:
                    old_display = old
                    new_display = new

                changes.append(
                    f"<li><b>{field_label}</b>: {old_display or '⌀'} → {new_display or '⌀'}</li>")

            if changes:
                message = _(
                    "%s <b>%s</b> has been updated after booking confirmation:<ul>%s</ul>"
                ) % (record._description, record.display_name, "".join(changes))
                for bk in confirmed_bookings:
                    bk.message_post(
                        partner_ids=bk.responsible_id.partner_id.ids,
                        body=message,
                    )

    def write(self, vals):

        if not self._validating_tracking_model():
            return super().write(vals)

        changed_fields = set(vals.keys()) & set(self._get_sensitive_fields_for_tracking_change_after_booking())
        old_values = {
            record.id: {
                field: record[field].id if record._fields[field].type == 'many2one' and record[field] else record[field]
                for field in changed_fields
            }
            for record in self
        } if changed_fields else {}

        res = super().write(vals)

        if changed_fields:
            self._log_sensitive_changes_to_booking(changed_fields, old_values)

        return res
