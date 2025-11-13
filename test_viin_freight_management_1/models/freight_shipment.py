import ast
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError, AccessDenied


class Shipment(models.Model):
    _name = 'freight.shipment'
    _description = 'Shipment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'freight.transport.mixin']
    _order = 'create_date desc, cutoff asc'

    def _default_cargo_mode(self):
        company = self.company_id or self.env.company
        return company.shipment_cargo_mode or 'simple_note'

    name = fields.Char(
        string='Shipment No.',
        required=True,
        copy=False,
        default=lambda self: _('New')
    )
    responsible_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)

    # Bill Of Lading
    house_bill_number = fields.Char(
        string='House Bill of Lading', tracking=True,
        help="Bill of Lading for this shipment, issued by Forwarder")
    master_bill_number = fields.Char(
        string='Master Bill of Lading', tracking=True,
        help="Bill of Lading for this shipment, issued by Carrier")

    multiple_leg_route = fields.Boolean(
        string='Multiple Leg Route',
        default=False,
        help="Tick this if the shipment is not a direct route and requires multiple transport legs. "
            "You'll be able to define each leg, carrier, and schedule.")
    shipping_method = fields.Char(string='Shipping Method',
        compute='_compute_shipping_method', store=True,
        help="This technical field is used to display the shipping method of the shipment reports"
    )

    # Stage Management
    stage_ids = fields.Many2many(
        'freight.shipment.stage', 'freight_shipment_stage_rel', 'shipment_id', 'stage_id',
        string='Stages', help="Stages that this shipment will go through")
    current_stage_id = fields.Many2one(
        'freight.shipment.stage', string='Current Stage', tracking=True,
        domain="[('id', 'in', stage_ids)]", group_expand='_read_group_stage_ids',
        help="Current stage of the shipment")

    # Computed stage-based states
    is_closed = fields.Boolean(string='Is Closed', compute='_compute_stage_states', store=True)
    delivery_status = fields.Selection([
        ('early', 'Early'),
        ('on_time', 'On Time'),
        ('late', 'Late'),
        ('in_transit', 'In Transit'),
    ], string='Delivery Status', compute='_compute_delivery_timing_status', store=True, tracking=True,
        help="Automatically determine if this shipment is on time, late, or early based on ETA and actual completion date.")

    booking_ids = fields.One2many('freight.booking', 'shipment_id', string='Bookings')
    booking_id = fields.Many2one('freight.booking', string='Booking', compute='_compute_booking', store=True)
    booking_count = fields.Integer(string='Booking Count', compute='_compute_booking_count')
    freight_route_ids = fields.One2many('freight.route', 'shipment_id', string='Freight Routes')
    main_route_id = fields.Many2one('freight.route', string='Main Route', compute='_compute_main_route', store=True)
    shipment_tracking_ids = fields.One2many('freight.shipment.tracking', 'shipment_id', string='Shipment Trackings')
    sale_order_ids = fields.One2many('sale.order', 'shipment_id', string='Sales Orders')
    sale_order_line_ids = fields.One2many('sale.order.line', 'shipment_id', string='Sales Order Lines')

    # last tracking
    last_tracking_id = fields.Many2one('freight.shipment.tracking', string='Last Tracking', copy=False)
    last_tracking_status = fields.Selection(selection=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold'),
        ('to_define', 'Set Status'),
    ], string='Last Tracking Status', default='to_define', tracking=True, required=True,
        compute='_compute_last_tracking_status', store=True, readonly=False)
    booking_status = fields.Selection(selection=[
        ('not_booked', 'Not Booked'),
        ('booking_in_progress', 'Booking in Progress'),
        ('booked', 'Booked'),
    ], default='not_booked', compute='_compute_booking_status', store=True)

    # Schedule
    etd = fields.Datetime(compute='_compute_schedule', store=True, readonly=False,)

    eta = fields.Datetime(
        compute='_compute_schedule',
        store=True,
        readonly=False,
        help="Estimated Time of Departure and Arrival. The planned date and time when the shipment or transport is expected to leave and arrive at the destination."
    )

    cutoff = fields.Datetime(
        compute='_compute_schedule',
        store=True,
        readonly=False,
        help="Cut-off Time. The latest date and time by which the cargo or container must be delivered to the terminal/warehouse to ensure the shipment can be loaded and depart as scheduled."
    )

    done_date = fields.Datetime(
        string='Done Date', copy=False, tracking=True,
        help="The moment the shipment is completed")

    cargo_mode = fields.Selection(
        selection=[
            ('simple_note', 'Quick Note Entry'),
            ('structured_entry', 'Detailed Structured Entry'),
        ],
        string='Cargo Input Mode', default=_default_cargo_mode,
        help="Choose how to input cargo details: free-style note or detailed structure."
    )
    cargo_template_ids = fields.One2many('cargo.template', 'shipment_id', string='Cargo Templates')
    package_ids = fields.One2many('freight.package', 'shipment_id', string='Packages')
    cargo_commodity_ids = fields.One2many('cargo.commodity', 'shipment_id', string='Cargo Details')
    cargo_note_details = fields.Text(string='Cargo Note Details', help="Free-form text to summarize cargo details.")

    # technical fields
    can_generate_bookings = fields.Boolean(string='Can Generate Bookings', compute='_compute_can_generate_bookings')
    has_templates_to_generate = fields.Boolean(string='Has Templates to Generate', compute='_compute_has_templates_to_generate')
    transport_mode_icon = fields.Char(string='Transport Mode Icon', compute='_compute_transport_mode_icon')
    third_party_ids = fields.Many2many('res.partner', string='Third Parties', compute='_compute_third_party')
    visible_quotation_button = fields.Boolean(string='Visible Quotation Button', compute='_compute_visible_quotation_button')

    display_origin = fields.Many2one(
        'res.partner',
        string='Display Origin',
        compute='_compute_display_locations',
        compute_sudo=True
    )
    display_destination = fields.Many2one(
        'res.partner',
        string='Display Destination',
        compute='_compute_display_locations',
        compute_sudo=True
    )
    display_carrier = fields.Many2one(
        'res.partner',
        string='Display Carrier',
        compute='_compute_display_carrier',
        compute_sudo=True
    )
    display_carrier_name = fields.Char(
        string='Display Carrier Name',
        compute='_compute_display_carrier',
        compute_sudo=True
    )
    is_multi_carrier = fields.Boolean(
        string='Has Multiple Carriers',
        compute='_compute_display_carrier',
        compute_sudo=True
    )

    analytic_account_id = fields.Many2one(related='sale_order_id.analytic_account_id', store=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
    )
    balance = fields.Monetary(related='analytic_account_id.balance', currency_field='currency_id')

    # ===============================================
    # ============ Constraints Methods ==============
    # ===============================================
    @api.constrains('sale_order_id')
    def _check_multiple_shipments(self):
        for record in self:
            if record.sale_order_id and len(record.sale_order_id.shipment_ids) > 1:
                raise ValidationError(_('Each sales order is created to serve only 1 shipment.\n'
                    "Sales order %s is currently trying to set up 2 shipments for the same sales order, please adjust it.\n"
                    "If you want to create a new shipment, create a new sales order")
                    % record.sale_order_id.name)

    @api.constrains('freight_route_ids')
    def _check_freight_route_ids(self):
        for record in self:
            main_route = record.freight_route_ids.filtered(lambda r: r.route_type == 'main_carriage')
            if len(main_route) > 1:
                raise ValidationError(_('The shipment can only have one main carriage route.'))

    @api.constrains('transport_mode', 'multiple_leg_route')
    def _check_transport_mode_and_multiple_leg_route(self):
        for record in self:
            if record.transport_mode == 'multiple' and not record.multiple_leg_route:
                raise ValidationError(_('The shipment must have multiple leg routes if the transport mode is multiple.'))

    # ===============================================
    # ============ Compute Methods ==================
    # ===============================================
    @api.depends('booking_ids')
    def _compute_booking(self):
        for record in self:
            record.booking_id = record.booking_ids[0] if record.booking_ids else False

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        read_group = self.env['freight.booking'].read_group(
            [('shipment_id', 'in', self.ids)],
            ['shipment_id'],
            ['shipment_id']
        )
        booking_count_data = {
            booking['shipment_id'][0]: booking['shipment_id_count']
            for booking in read_group
        }
        for record in self:
            record.booking_count = booking_count_data.get(record.id, 0)

    @api.depends('cargo_commodity_ids', 'package_ids')
    def _compute_counts(self):
        package_read_group = self.env['freight.package'].read_group(
            [('shipment_id', 'in', self.ids)],
            ['shipment_id'],
            ['shipment_id']
        )
        package_count_data = {
            package['shipment_id'][0]: package['shipment_id_count']
            for package in package_read_group
        }

        cargo_commodity_read_group = self.env['cargo.commodity'].read_group(
            [('shipment_id', 'in', self.ids)],
            ['shipment_id', 'quantity'],
            ['shipment_id']
        )
        cargo_commodity_count_data = {
            cargo_commodity['shipment_id'][0]: cargo_commodity['quantity']
            for cargo_commodity in cargo_commodity_read_group
        }

        for record in self:
            record.total_packages = package_count_data.get(record.id, 0)
            if record.cargo_mode == 'structured_entry':
                record.total_cargo_commodities = cargo_commodity_count_data.get(record.id, 0)

    @api.depends('cargo_commodity_ids.weight', 'cargo_commodity_ids.volume', 'package_ids.volume', 'package_ids.weight')
    def _compute_cargo_totals(self):
        super()._compute_cargo_totals()
        for record in self:
            if record.package_ids:
                record.total_weight = sum(record.package_ids.mapped('weight'))
                record.total_volume = sum(record.package_ids.mapped('volume'))
            elif record.cargo_commodity_ids:
                record.total_weight = sum(record.cargo_commodity_ids.mapped('weight'))
                record.total_volume = sum(record.cargo_commodity_ids.mapped('volume'))

    @api.depends('agent_id', 'consignee_id', 'notify_party_id', 'shipper_id')
    def _compute_third_party(self):
        for r in self:
            r.third_party_ids = r.agent_id | r.consignee_id | r.notify_party_id | r.shipper_id

    @api.depends(
        'freight_route_ids',
        'freight_route_ids.eta',
        'freight_route_ids.etd',
        'freight_route_ids.cutoff',
        'multiple_leg_route'
    )
    def _compute_schedule(self):
        for record in self:
            if record.multiple_leg_route:
                if record.freight_route_ids:
                    # Use safe approach with list comprehension to avoid error on empty sequence
                    route_etds = [route.etd for route in record.freight_route_ids if route.etd]
                    route_etas = [route.eta for route in record.freight_route_ids if route.eta]
                    route_cutoffs = [route.cutoff for route in record.freight_route_ids if route.cutoff]

                    record.etd = min(route_etds) if route_etds else False
                    record.eta = max(route_etas) if route_etas else False
                    record.cutoff = min(route_cutoffs) if route_cutoffs else False
                else:
                    # Multiple leg route is enabled but no routes defined yet
                    record.etd = False
                    record.eta = False
                    record.cutoff = False

    @api.depends('transport_mode')
    def _compute_transport_mode_icon(self):
        for record in self:
            if not record.transport_mode:
                record.transport_mode_icon = 'fa-globe'
            elif 'sea' in record.transport_mode.lower():
                record.transport_mode_icon = 'fa-ship'
            elif 'air' in record.transport_mode.lower():
                record.transport_mode_icon = 'fa-plane'
            elif 'land' in record.transport_mode.lower():
                record.transport_mode_icon = 'fa-truck'
            else:
                record.transport_mode_icon = 'fa-exchange'

    @api.depends('current_stage_id', 'current_stage_id.is_closed')
    def _compute_stage_states(self):
        for record in self:
            record.is_closed = record.current_stage_id.is_closed

    @api.depends('package_ids.booking_status', 'cargo_commodity_ids.booking_status')
    def _compute_can_generate_bookings(self):
        for record in self:
            if any(package.booking_status == 'need_booking' for package in record.package_ids):
                record.can_generate_bookings = True
            elif any(cargo.booking_status == 'need_booking' for cargo in record.cargo_commodity_ids):
                record.can_generate_bookings = True
            else:
                record.can_generate_bookings = False

    @api.depends('cargo_template_ids.is_generated')
    def _compute_has_templates_to_generate(self):
        for record in self:
            record.has_templates_to_generate = any(not cargo_template.is_generated for cargo_template in record.cargo_template_ids)

    @api.depends('multiple_leg_route', 'origin_id', 'destination_id', 'freight_route_ids.origin_id', 'freight_route_ids.destination_id')
    def _compute_display_locations(self):
        for record in self:
            if not record.multiple_leg_route:
                record.display_origin = record.origin_id
                record.display_destination = record.destination_id
            else:
                routes = record.freight_route_ids.sorted('sequence')
                record.display_origin = routes[0].origin_id if routes else False
                record.display_destination = routes[-1].destination_id if routes else False

    @api.depends('multiple_leg_route', 'carrier_id', 'freight_route_ids.carrier_id')
    def _compute_display_carrier(self):
        for record in self:
            if not record.multiple_leg_route:
                record.display_carrier = record.carrier_id
                record.is_multi_carrier = False
                record.display_carrier_name = record.carrier_id.name if record.carrier_id else ''
            else:
                carriers = record.freight_route_ids.mapped('carrier_id')
                if len(carriers) == 1:
                    record.display_carrier = carriers[0]
                    record.is_multi_carrier = False
                    record.display_carrier_name = carriers[0].name if carriers else ''
                else:
                    # Multiple carriers case
                    record.display_carrier = False
                    record.is_multi_carrier = True
                    record.display_carrier_name = ', '.join(carriers.mapped('name')) if carriers else ''

    @api.depends('last_tracking_id.status')
    def _compute_last_tracking_status(self):
        for record in self:
            if record.last_tracking_id:
                record.last_tracking_status = record.last_tracking_id.status
            else:
                record.last_tracking_status = 'to_define'

    @api.depends('booking_ids.state')
    def _compute_booking_status(self):
        for record in self:
            bookings = record.booking_ids
            if not bookings:
                record.booking_status = 'not_booked'
            elif all(booking.state == 'done' for booking in bookings):
                record.booking_status = 'booked'
            else:
                record.booking_status = 'booking_in_progress'

    @api.depends('freight_route_ids.route_type')
    def _compute_main_route(self):
        for r in self:
            main_route = r.freight_route_ids.filtered(lambda route: route.route_type == 'main_carriage')
            r.main_route_id = main_route[:1]

    @api.depends('freight_route_ids.transport_mode',
                 'freight_route_ids.ocean_shipping_method_id',
                 'freight_route_ids.air_shipping_method_id',
                 'freight_route_ids.land_shipping_method_id')
    def _compute_shipping_method(self):
        for shipment in self:
            methods = set()
            for route in shipment.freight_route_ids:
                method = (
                    route.ocean_shipping_method_id.name or
                    route.air_shipping_method_id.name or
                    route.land_shipping_method_id.name
                )
                if method:
                    methods.add(method)
            if len(methods) == 1:
                shipment.shipping_method = list(methods)[0]
            elif len(methods) > 1:
                shipment.shipping_method = _('Multiple')
            else:
                shipment.shipping_method = _('Not Defined')

    @api.depends('done_date', 'eta')
    def _compute_delivery_timing_status(self):
        for record in self:
            if record.done_date and record.eta:
                if record.done_date > record.eta:
                    record.delivery_status = 'late'
                elif record.done_date < record.eta:
                    record.delivery_status = 'early'
                else:
                    record.delivery_status = 'on_time'
            else:
                record.delivery_status = 'in_transit'

    @api.depends('sale_order_id', 'multiple_leg_route', 'freight_route_ids.route_id', 'route_id')
    def _compute_visible_quotation_button(self):
        for record in self:
            if record.sale_order_id:
                record.visible_quotation_button = False
            else:
                if record.multiple_leg_route:
                    if record.freight_route_ids.route_id:
                        record.visible_quotation_button = True
                    else:
                        record.visible_quotation_button = False
                else:
                    record.visible_quotation_button = record.route_id

    @api.onchange('transport_mode')
    def _onchange_transport_mode(self):
        if self.transport_mode == 'multiple':
            self.multiple_leg_route = True

    # ===============================================
    # ============ CRUD Methods =====================
    # ===============================================
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Read all the stages and display them in the kanban view,
        even if they are empty"""
        stage_ids = stages._search([])
        return stages.browse(stage_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial stage and generate sequence for shipment number"""
        first_stage = self.env['freight.shipment.stage'].search([], order='sequence asc', limit=1)

        for vals in vals_list:
            if first_stage:
                if not vals.get('current_stage_id'):
                    vals['current_stage_id'] = first_stage.id
                if not vals.get('stage_ids'):
                    vals['stage_ids'] = [(4, first_stage.id)]
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('freight.shipment') or _('New')

        shipments = super(Shipment, self).create(vals_list)

        for shipment in shipments:
            if not shipment.multiple_leg_route:
                shipment._create_of_update_main_route()
        return shipments

    def write(self, vals):
        res = super().write(vals)

        if 'current_stage_id' in vals:
            stage = self.env['freight.shipment.stage'].browse(vals['current_stage_id'])
            if stage.is_closed:
                self.done_date = fields.Datetime.now()
            else:
                self.done_date = False

        if not self.multiple_leg_route and any(f in vals for f in self._get_main_leg_route_update_fields()):
            self._create_of_update_main_route()

        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_check_booking_ids(self):
        """Override unlink method to check if the shipment has a booking"""
        for record in self:
            if record.booking_ids:
                raise UserError(_("You cannot delete shipment %s that has bookings. please delete all bookings related to this shipment first.") % record.name)

    # ================================================
    # ============ Business Methods ==================
    # ================================================

    def _get_sensitive_fields_for_tracking_change_after_booking(self):
        return self._get_core_transport_info_fields() + ['shipper_id', 'mbl', 'hbl']

    def _get_booking_records(self):
        """
        Get the booking records for this shipment.
        """
        return self.booking_ids

    def _get_main_leg_route_update_fields(self):
        """
        Returns a list of fields that, when updated, should trigger the
        update of the main leg route for single-leg shipments.
        """
        return self._get_core_transport_info_fields() + ['route_id', 'package_ids', 'cargo_commodity_ids']

    def _get_revenue_lines(self):
        """Hook method to get the revenue lines for the shipment profitability report.
        Can be overridden in other modules to include or exclude specific lines.
        """
        self.ensure_one()
        if self.sale_order_id:
            return self.sale_order_id.order_line.filtered(lambda l: not l.display_type and l.price_subtotal > 0)
        return self.env['sale.order.line']

    def _prepare_revenue_line_vals(self, line):
        """Hook method to prepare the values for a single revenue line.
        This allows for customization of the displayed data, for example,
        by adding flags for special line types (e.g., collection services).
        """
        return {
            'id': line.id,
            'name': line.name,
            'billed_amount': line.untaxed_amount_invoiced,
            'to_bill_amount': line.untaxed_amount_to_invoice,
            'amount': line.price_subtotal,
            'is_excluded_from_profit': False,  # Default value
        }

    def _get_cost_lines(self):
        """Hook method to get the cost lines for the shipment profitability report."""
        self.ensure_one()
        if self.analytic_account_id:
            return self.analytic_account_id.line_ids.filtered(lambda l: l.amount < 0)
        return self.env['account.analytic.line']

    def _get_cost_billed_amounts(self, line):
        """
        Hook method to determine the billed and to-bill amounts for a cost line.
        In this base module, we assume all costs are "to_bill" by default.
        This can be overridden in other modules (e.g., viin_freight_management_project)
        to implement specific billing logic.
        """
        cost_amount = -line.amount
        return {'billed': 0.0, 'to_bill': cost_amount}

    def _prepare_cost_line_vals(self, line):
        """Hook method to prepare the values for a single cost line."""
        billed_amounts = self._get_cost_billed_amounts(line)
        return {
            'id': line.id,
            'name': line.name,
            'billed_amount': billed_amounts['billed'],
            'to_bill_amount': billed_amounts['to_bill'],
            'amount': billed_amounts['billed'] + billed_amounts['to_bill'],
            'ref': line.ref,
            'date': line.date,
        }

    def _get_profitability_data(self):
        """
        Gathers profitability data for the shipment, including revenue and cost lines.

        For each shipment, this method compiles detailed information about revenues and costs,
        categorizing them into billed/invoiced and to-be-billed/to-be-invoiced amounts.
        It retrieves revenue lines from associated sales order lines and cost lines from
        vendor bills linked via an analytic account.

        The method calculates totals for both revenues and costs, providing a clear
        financial overview of the shipment's performance. It also includes currency
        information to ensure proper formatting on the client-side.

        Returns:
            dict: A dictionary containing profitability data for each shipment.
                The keys are shipment IDs, and the values are dictionaries with the
                following structure:
                - 'currency_id': The currency ID for monetary values.
                - 'revenues': A dictionary with 'data' (a list of revenue line details) and 'total' amounts.
                - 'costs': A dictionary with 'data' (a list of cost line details) and 'total' amounts.
        """
        shipment_data = {}
        for shipment in self:
            # Initialize data structure for each shipment
            all_revenue_lines_vals = [self._prepare_revenue_line_vals(line) for line in shipment._get_revenue_lines()]
            cost_lines_vals = [self._prepare_cost_line_vals(line) for line in shipment._get_cost_lines()]

            # Partition revenue lines into actual revenues and on-behalf items
            revenue_lines_vals = []
            on_behalf_lines_vals = []
            for line in all_revenue_lines_vals:
                if line.get('is_excluded_from_profit'):
                    on_behalf_lines_vals.append(line)
                else:
                    revenue_lines_vals.append(line)

            shipment_data[shipment.id] = {
                'currency_id': shipment.currency_id.id,
                'revenues': {
                    'data': revenue_lines_vals,
                    'total': {
                        'billed': sum(line['billed_amount'] for line in revenue_lines_vals),
                        'to_bill': sum(line['to_bill_amount'] for line in revenue_lines_vals),
                        'expected': sum(line['amount'] for line in revenue_lines_vals),
                    },
                },
                'costs': {
                    'data': cost_lines_vals,
                    'total': {
                        'billed': sum(line['billed_amount'] for line in cost_lines_vals),
                        'to_bill': sum(line['to_bill_amount'] for line in cost_lines_vals),
                        'expected': sum(line['amount'] for line in cost_lines_vals),
                    },
                },
                'on_behalf_items': {
                    'data': on_behalf_lines_vals,
                    'total': {
                        'billed': sum(line['billed_amount'] for line in on_behalf_lines_vals),
                        'to_bill': sum(line['to_bill_amount'] for line in on_behalf_lines_vals),
                        'expected': sum(line['amount'] for line in on_behalf_lines_vals),
                    }
                }
            }
        return shipment_data

    def get_panel_data(self):
        """
        Gathers all necessary data for the shipment right side panel.
        """
        self.ensure_one()

        profitability_data = self._get_profitability_data()[self.id]

        panel_data = {
            'shipment_id': self.id,
            'shipment_name': self.name,
            'sale_order_id': self.sale_order_id.id,
            'sale_order_name': self.sale_order_id.name,
            'sale_order_line_ids': self.sale_order_id.order_line.ids,
            'booking_count': self.booking_count,
            'booking_ids': self.booking_ids.ids,
            'currency_id': self.currency_id.id,
            'currency_decimal_places': self.currency_id.decimal_places,
            'profitability_items': {
                'revenues': profitability_data.get('revenues'),
                'costs': profitability_data.get('costs'),
            },
            'on_behalf_items': profitability_data.get('on_behalf_items'),
        }
        return panel_data

    def get_shipment_datas(self):
        return self._get_profitability_data()

    # ===============================================
    # ============ Business Methods =================
    # ===============================================
    def action_send_email_for_party(self):
        """Send email to notify party when shipment arrives"""
        pass

    def _create_of_update_main_route(self):
        for record in self:
            if record.multiple_leg_route:
                continue
            if not record.main_route_id:
                self.env['freight.route'].create(record._prepare_main_leg_route_vals())
            else:
                record.main_route_id.write(record._prepare_main_leg_route_vals())

    def _prepare_main_leg_route_vals(self):
        self.ensure_one()
        return {
            'shipment_id': self.id,
            'route_id': self.route_id.id,
            'route_type': 'main_carriage',
            'carrier_id': self.carrier_id.id,
            'agent_id': self.agent_id.id,
            'consignee_id': self.consignee_id.id,
            'notify_party_id': self.notify_party_id.id,
            'shipper_id': self.shipper_id.id,
            'origin_id': self.origin_id.id,
            'destination_id': self.destination_id.id,
            'etd': self.etd,
            'eta': self.eta,
            'cutoff': self.cutoff,
            'transport_mode': self.transport_mode,
            'service_type': self.service_type,
            'ocean_shipping_method_id': self.ocean_shipping_method_id.id,
            'air_shipping_method_id': self.air_shipping_method_id.id,
            'land_shipping_method_id': self.land_shipping_method_id.id,
            'package_ids': [(6, 0, self.package_ids.ids)],
            'cargo_commodity_ids': [(6, 0, self.cargo_commodity_ids.ids)],
            'sale_order_line_id': self.sale_order_line_id.id,
        }

    def action_view_packages(self):
        self.ensure_one()
        return {
            'name': _('Packages'),
            'view_mode': 'tree,form',
            'res_model': 'freight.package',
            'domain': [('id', 'in', self.package_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': {'default_shipment_id': self.id}
        }

    def action_view_cargo_commodities(self):
        self.ensure_one()
        return {
            'name': _('Cargo Commodities'),
            'view_mode': 'tree,form',
            'res_model': 'cargo.commodity',
            'domain': [('id', 'in', self.cargo_commodity_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': {'default_shipment_id': self.id}
        }

    def action_view_bookings(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_booking')
        action['context'] = {'default_shipment_id': self[:1].id}
        if len(self.booking_ids) == 1:
            form = self.env.ref('viin_freight_management.freight_booking_view_form')
            action['views'] = [(form and form.id or False, 'form')]
            action['res_id'] = self.booking_ids.id
        elif len(self.booking_ids) > 1:
            action['domain'] = [('shipment_id', 'in', self.ids)]
        return action

    def action_view_progress(self):
        """ return the action to see the overview report of the shipment """
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_shipment_progress_report')
        action['display_name'] = _("%(name)s's Overview", name=self.name)
        action_context = ast.literal_eval(action['context']) if action['context'] else {}
        action_context['search_default_shipment_id'] = self.id
        action['context'] = action_context
        return action

    def action_view_profitability(self):
        """ return the action to see the profitability report of the shipment """
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_shipment_profitability_report')
        action['display_name'] = _("%(name)s's Profitability", name=self.name)
        action_context = ast.literal_eval(action['context']) if action['context'] else {}
        action_context['search_default_shipment_id'] = self.id
        action['context'] = action_context
        return action

    def action_view_gross_margin(self):
        """
        View gross margin for the shipment
        """
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action')
        action['domain'] = [('account_id', '=', self.analytic_account_id.id)]
        return action

    def generator_from_cargo_templates(self):
        """
        Automatically generate freight shipments or packages from unprocessed cargo templates linked to this shipment.

        This method is used when the cargo templates exist but their corresponding cargo details (shipments or packages)
        have not been created yet. Without this automation, users would need to manually create each freight shipment or
        package one by one based on the cargo template information, which is tedious and error-prone.

        Typically, this action is triggered by logistics coordinators or warehouse operators after confirming
        the cargo templates but before finalizing booking and shipment arrangements.
        """
        self.ensure_one()
        need_generate_cargo_templates = self.cargo_template_ids.filtered(lambda r: not r.is_generated)
        return need_generate_cargo_templates._generator_to_cargo_details()

    def action_generate_bookings(self):
        """
        Generate bookings for packages in the shipment that need booking.

        This method groups packages by route and carrier to create optimal bookings.
        For each group of packages, a booking is created with the appropriate carrier and route.

        This approach ensures that:
        1. All packages that need booking are properly handled
        2. Packages are grouped efficiently by carrier and route
        3. The booking structure matches the physical transport plan

        After bookings are created, the method returns an action to open and review the generated bookings.
        """
        booking_vals_list = []

        for record in self:
            # Identify packages that need booking based on their booking_status
            need_booking_packages = record.package_ids.filtered(
                lambda p: p.booking_status == 'need_booking')
            need_booking_cargo_commodities = record.cargo_commodity_ids.filtered(
                lambda c: c.booking_status == 'need_booking')

            if record.multiple_leg_route and not record.freight_route_ids:
                raise ValidationError(
                    _('Please define at least one route for multiple leg shipment %s.') % record.name)

            if need_booking_packages:
                package_booking_vals_list = need_booking_packages._prepare_booking_vals()
                if package_booking_vals_list:
                    booking_vals_list.extend(package_booking_vals_list)

            elif need_booking_cargo_commodities:
                cargo_commodity_booking_vals_list = need_booking_cargo_commodities._prepare_booking_vals()
                if cargo_commodity_booking_vals_list:
                    booking_vals_list.extend(cargo_commodity_booking_vals_list)

        # Create bookings from the prepared values
        if booking_vals_list:
            self.env['freight.booking'].create(booking_vals_list)

        return self.action_view_bookings()

    def action_update_shipment_tracking(self):
        self.ensure_one()
        return {
            'name': _('Shipment Tracking'),
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment.tracking',
            'view_mode': 'form',
            'view_id': self.env.ref('viin_freight_management.shipment_tracking_form_view').id,
            'target': 'new',
            'context': {
                'default_shipment_id': self.id,
                'default_stage_id': self.current_stage_id.id,
                'default_notify_to_partner_ids': self.third_party_ids.ids,
            }
        }

    def action_view_shipment_tracking(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_shipment_tracking')
        action['context'] = {
            'default_shipment_id': self.id,
            'default_stage_id': self.current_stage_id.id,
            'default_notify_to_partner_ids': self.third_party_ids.ids,
        }
        action['domain'] = [('shipment_id', '=', self.id)]
        return action

    def _check_delivery_status(self):
        """
        Return True if all shipment routes are done, allowing automatic confirmation of shipment ATA.
        Otherwise, the shipment remains pending until the last route is completed.
        """
        self.ensure_one()
        return all(route.freight_status == 'done' for route in self.freight_route_ids)

    def action_portal_preview(self):
        self.ensure_one()
        return {
            'name': _('Shipment Preview'),
            'type': 'ir.actions.act_url',
            'url': '/my/shipment/%s' % self.id,
            'target': 'self',
        }

    def action_view_sale_order(self):
        self.ensure_one()
        all_sale_orders = self.sale_order_ids
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            'name': _("%(name)s's Sales Order", name=self.name),
            "context": {"create": False, "show_sale": True},
        }
        if len(all_sale_orders) == 1:
            action_window.update({
                "res_id": all_sale_orders.id,
                "views": [[False, "form"]],
            })
        else:
            action_window.update({
                "domain": [('id', 'in', all_sale_orders.ids)],
                "views": [[False, "tree"], [False, "kanban"], [False, "calendar"], [False, "pivot"],
                    [False, "graph"], [False, "activity"], [False, "form"]],
            })
        return action_window

    def action_generator_quotation(self):
        self.ensure_one()
        order_line_vals_list = []
        if self.multiple_leg_route:
            for route in self.freight_route_ids:
                order_line_vals_list.append(route._prepare_order_line_vals())
        else:
            order_line_vals_list.append(self._prepare_order_line_vals())
        order_values = {
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'shipment_id': self.id,
            'shipment_ids': [(6, 0, self.ids)],
            'order_line': [
                (0, 0, vals) for vals in order_line_vals_list
            ],

        }
        order = self.env['sale.order'].create(order_values)

        if self.multiple_leg_route:
            for route, order_line in zip(self.freight_route_ids, order.order_line):
                route.write({'sale_order_line_id': order_line.id})

        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
            return self.action_view_sale_order()
        except(AccessError, AccessDenied):
            return

    def _prepare_order_line_vals(self):
        self.ensure_one()
        product = self.route_id.product_ids.filtered(
                lambda p: p.detailed_type == 'freight' and
                p.transport_mode == self.transport_mode and
                p.ocean_shipping_method_id == self.ocean_shipping_method_id and
                p.air_shipping_method_id == self.air_shipping_method_id and
                p.land_shipping_method_id == self.land_shipping_method_id
            )[:1]
        if product:
            return {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': len(self.package_ids) if self.package_ids else 1,
                'shipment_id': self.id,
            }
        else:
            raise ValidationError(_(
                "No suitable freight product found for shipment %s, "
                "please contact the administrator to add a freight product.") % self.name)

    def _get_report_base_filename(self):
        """
        Get the base filename for the report when printing or downloading.
        """
        self.ensure_one()
        return f'HBL_{self.name}'

    def _get_report_attachment_filename(self):
        """
        Get the attachment filename for caching the report.
        Return False to disable caching and always regenerate the report.
        """
        return False
