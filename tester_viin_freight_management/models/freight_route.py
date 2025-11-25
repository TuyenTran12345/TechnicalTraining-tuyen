from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FreightRoute(models.Model):
    _name = 'freight.route'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'freight.transport.mixin']
    _description = 'Freight Route'
    _order = 'sequence, id'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        shipment_id = self.env.context.get('active_shipment_id', False)
        if shipment_id:
            shipment = self.env['freight.shipment'].browse(shipment_id)
            if not res.get('notify_party_id'):
                res['notify_party_id'] = shipment.notify_party_id.id
            if not res.get('package_ids'):
                res['package_ids'] = [(6, 0, shipment.package_ids.ids)]
        return res

    name = fields.Char(string='Name', required=True, copy=False, default=lambda self: _('New'), help="Internal reference name for the freight route. Auto-generated based on sequence, transport mode, and shipment.")
    sequence = fields.Integer(string='Sequence', default=10, help="Sequence number to control the order of multiple legs in a shipment")
    route_type = fields.Selection([
        ('pickup', 'Pickup'),
        ('domestic_carriage', 'Domestic Carriage'),
        ('pre_carriage', 'Pre-carriage'),
        ('main_carriage', 'Main carriage'),
        ('on_carriage', 'On-carriage'),
        ('delivery', 'Delivery')
    ], string='Route Type',
        help="Define the type of this transport leg within the shipment:\n"
            "- Pickup: Collect cargo from the shipper's location.\n"
            "- Domestic Carriage: Transport within the country, not part of international main transport.\n"
            "- Pre-carriage: Inland transport from origin point to the port of export.\n"
            "- Main Carriage: Main international transport leg (e.g., sea freight, air freight).\n"
            "- On-carriage: Inland transport after cargo arrives at the port of import.\n"
            "- Delivery: Final delivery to the consignee's location.")
    # todo: change me to progress or stage.
    freight_status = fields.Selection([
        ('planned', 'Planned'),
        ('in_transit', 'In Transit'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Freight Status', default='planned', tracking=True,
        help="Current transport progress for this route:\n"
            "- Planned: Transport is scheduled but not yet started.\n"
            "- In Transit: Cargo is currently being moved on this route.\n"
            "- Done: Cargo has completed transport and was successfully delivered.\n"
            "- Cancelled: The planned transport for this route has been cancelled.")

    # References
    shipment_id = fields.Many2one('freight.shipment', string='Shipment')
    booking_ids = fields.Many2many(
        'freight.booking', 'freight_route_booking_rel', 'route_id', 'booking_id',
        string='Bookings'
    )
    cargo_mode = fields.Selection(related='shipment_id.cargo_mode')
    package_ids = fields.Many2many(
        'freight.package', 'freight_route_package_rel', 'route_id', 'package_id',
        string='Packages',
    )
    cargo_commodity_ids = fields.Many2many(
        'cargo.commodity', 'freight_route_cargo_commodity_rel', 'route_id', 'cargo_commodity_id', string='Cargo Commodities',
        compute='_compute_cargo_commodity_ids', store=True, readonly=False
    )
    cargo_note_details = fields.Text(
        string='Cargo Note Details',
        help="Free-form text to summarize cargo details.",
        compute='_compute_cargo_note_details',
        store=True,
        readonly=False
    )

    shipper_id = fields.Many2one(related='shipment_id.shipper_id')
    consignee_id = fields.Many2one(related='shipment_id.consignee_id')
    third_party_ids = fields.Many2many('res.partner', string='Third Parties', compute='_compute_third_party')

    # last tracking
    last_tracking_id = fields.Many2one('freight.shipment.tracking', string='Last Tracking', copy=False)
    last_tracking_status = fields.Selection(selection=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold'),
        ('to_define', 'Set Status'),
    ], default='to_define', compute='_compute_last_tracking_status', store=True, readonly=False, required=True)

    def _compute_display_name(self):
        # Define route type display mapping
        route_type_mapping = {
            'pickup': 'PICKUP',
            'domestic_carriage': 'DOMESTIC',
            'pre_carriage': 'PRE',
            'main_carriage': 'MAIN',
            'on_carriage': 'ON',
            'delivery': 'DELIV'
        }

        super()._compute_display_name()
        for record in self:
            route_type_label = route_type_mapping.get(record.route_type, record.route_type)
            if record.route_id:
                origin_destination_label = record.route_id.name
            elif record.origin_id and record.destination_id:
                origin_destination_label = f"{record.origin_id.name} - {record.destination_id.name}"
            else:
                origin_destination_label = record.shipment_id.name
            record.display_name = f"[{route_type_label}] {origin_destination_label}"

    # ===============================================
    # ============ Constraints =====================
    # ===============================================
    @api.constrains('route_type', 'shipment_id')
    def _check_route_type(self):
        for record in self:
            shipment = record.shipment_id
            if shipment.multiple_leg_route and len(shipment.freight_route_ids.filtered(lambda r: r.route_type == 'main_carriage')) > 1:
                raise ValidationError(_("The shipment can only have one main carriage route."))

    # ===============================================
    # ============ Compute Methods ==================
    # ===============================================

    @api.depends('package_ids.cargo_commodity_ids')
    def _compute_cargo_commodity_ids(self):
        for route in self:
            if route.package_ids:
                route.cargo_commodity_ids = route.package_ids.cargo_commodity_ids

    @api.depends('package_ids.cargo_note_details')
    def _compute_cargo_note_details(self):
        for route in self:
            if route.package_ids:
                notes = route.package_ids.mapped('cargo_note_details')
                route.cargo_note_details = '\n'.join(filter(None, notes))

    @api.depends('shipment_id.consignee_id', 'shipment_id.shipper_id', 'agent_id', 'notify_party_id')
    def _compute_third_party(self):
        for record in self:
            record.third_party_ids = record.agent_id | record.shipment_id.consignee_id | record.notify_party_id | record.shipment_id.shipper_id

    @api.depends('last_tracking_id')
    def _compute_last_tracking_status(self):
        for record in self:
            if record.last_tracking_id:
                record.last_tracking_status = record.last_tracking_id.status
            else:
                record.last_tracking_status = 'to_define'

    # ===============================================
    # ============ CRUD Methods =====================
    # ===============================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                sequence = self.env['ir.sequence'].next_by_code('freight.route')
                shipment_ref = 'NO-SHP'
                if vals.get('shipment_id'):
                    shipment = self.env['freight.shipment'].browse(vals['shipment_id'])
                    shipment_ref = shipment.name or 'NO-SHP'
                vals['name'] = f"{sequence}-{shipment_ref}"
        return super().create(vals_list)

    @api.ondelete(at_uninstall=False)
    def _unlink_validate_booking_state(self):
        for record in self:
            if record.booking_ids and any(b.state != 'draft' for b in record.booking_ids):
                raise ValidationError(_(
                    "You cannot delete a route %s that has a booking with status other than draft."
                    "If you want to delete it, please set status of booking %s for this route to Draft before deleting."
                ) % (record.name, ', '.join(record.booking_ids.mapped('name'))))

    # ===============================================
    # ============ Business Methods =================
    # ===============================================
    def _get_booking_records(self):
        """
        Get the booking records for this route.
        """
        return self.booking_ids

    def _get_port_vals_by_service_type(self):
        """
        Get the values for a single leg route
        @return: dict of route values
        """
        self.ensure_one()
        service_type = self.service_type
        location_vals = {}
        if service_type in ('port_to_port', 'door_to_door'):
            location_vals.update({
                'port_of_loading_id': self.origin_id.id,
                'port_of_discharge_id': self.destination_id.id,
            })
        elif service_type == 'door_to_port':
            location_vals.update({
                'port_of_discharge_id': self.destination_id.id,
            })
        elif service_type == 'port_to_door':
            location_vals.update({
                'port_of_loading_id': self.origin_id.id,
            })
        return location_vals

    def action_set_in_transit(self):
        """Set the freight status to in transit"""
        self.freight_status = 'in_transit'
        now = fields.Datetime.now()
        self.atd = now
        not_atd_shipments = self.shipment_id.filtered(lambda s: not s.atd)
        if not_atd_shipments:
            not_atd_shipments.write({'atd': now})

    def action_set_done(self):
        """Set the freight status to done"""
        self.freight_status = 'done'
        now = fields.Datetime.now()
        self.ata = now
        all_done_shipments = self.shipment_id.filtered(lambda s: s._check_delivery_status())
        if all_done_shipments:
            all_done_shipments.write({'ata': now})

    def action_set_cancelled(self):
        """Set the freight status to cancelled"""
        self.atd = False
        self.ata = False
        self.freight_status = 'cancelled'

    def action_set_planned(self):
        """Set the freight status to planned"""
        self.atd = False
        self.ata = False
        self.freight_status = 'planned'

    def action_update_shipment_tracking(self):
        """Update the shipment tracking"""
        self.ensure_one()
        action = self.shipment_id.action_update_shipment_tracking()
        context = action['context']
        context.update({
            'default_freight_route_id': self.id,
            'default_notify_to_partner_ids': self.third_party_ids.ids,
        })
        action['context'] = context
        return action

    def _prepare_order_line_vals(self):
        product = self.route_id.product_ids.filtered(
            lambda p: p.detailed_type == 'freight' and
            p.transport_mode == self.transport_mode and
            p.ocean_shipping_method_id == self.ocean_shipping_method_id and
            p.air_shipping_method_id == self.air_shipping_method_id and
            p.land_shipping_method_id == self.land_shipping_method_id
        )[:1]
        if product:
            return {
                'product_id': product.id,
                'product_uom_qty': len(self.package_ids) if self.package_ids else 1,
                'name': product.name,
                'shipment_id': self.shipment_id.id,
                'freight_route_id': self.id,
            }
        else:
            raise ValidationError(_(
                "No suitable freight product found for route %s or shipment %s, "
                "please contact the administrator to add a freight product.") % (self.name, self.shipment_id.name))
