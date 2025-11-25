from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_ids = fields.One2many('freight.booking', 'sale_order_id', string='Bookings', groups="viin_freight_management.group_freight_user")
    booking_count = fields.Integer(string='Bookings Count', compute='_compute_booking_count', groups="viin_freight_management.group_freight_user")
    shipment_ids = fields.One2many('freight.shipment', 'sale_order_id', string='Shipments', groups="viin_freight_management.group_freight_user")
    shipment_id = fields.Many2one('freight.shipment', string='Shipment', groups="viin_freight_management.group_freight_user",
        domain="[('sale_order_id', '=', False)]", help="Choose the existing shipment for this sales order to be used for freight services.")
    shipment_count = fields.Integer(string='Shipments Count', compute='_compute_shipment_count', groups="viin_freight_management.group_freight_user")
    direction = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ('domestic', 'Domestic')
    ], string='Direction', compute='_compute_transport_data', store=True,
        groups="viin_freight_management.group_freight_user")

    transport_mode = fields.Selection([
        ('sea', 'Sea Freight'),
        ('air', 'Air Freight'),
        ('land', 'Land Transport'),
        ('multiple', 'Multi-modal'),
    ], string='Transport Mode', compute='_compute_transport_data', store=True,
        groups="viin_freight_management.group_freight_user")

    ocean_shipping_method_id = fields.Many2one('freight.shipping.method', string='Ocean Shipping Method',
        compute='_compute_transport_data', store=True,
        groups="viin_freight_management.group_freight_user")
    air_shipping_method_id = fields.Many2one('freight.shipping.method', string='Air Shipping Method',
        compute='_compute_transport_data', store=True,
        groups="viin_freight_management.group_freight_user")
    land_shipping_method_id = fields.Many2one('freight.shipping.method', string='Land Shipping Method',
        compute='_compute_transport_data', store=True,
        groups="viin_freight_management.group_freight_user")

    freight_route_ids = fields.One2many('freight.route', 'sale_order_id', string='Routes', groups="viin_freight_management.group_freight_user")

    visible_shipment = fields.Boolean('Display shipment', compute='_compute_visible_shipment', compute_sudo=True)
    mismatched_fields_warning = fields.Html(
        string='Data Mismatch Warning', compute='_compute_mismatched_fields', compute_sudo=True,
        help="This field is used to display a warning message when the data of the sales order is not match with the "
            "shipment data. It help user to check if the shipment data is correct and if not, update the shipment data "
            "to match the sales order data.")

    # technical fields
    is_freight = fields.Boolean(string='Is Freight', compute='_compute_is_freight',
        help="Technical field indicating whether this sales order involves freight services.")

    @api.constrains('shipment_ids')
    def _check_multiple_shipments(self):
        """
        Ensure that each sales order is linked to only one shipment.
        This constraint prevents accidental duplication of shipments for the same sales order,
        maintaining a clean one-order-one-shipment relationship for freight workflows.
        """
        for r in self:
            if len(r.shipment_ids) > 1:
                raise UserError(
                    _("Each sales order is created to serve only 1 shipment.\n"
                    "Sales order %s is currently trying to set up 2 shipments for the same sales order, please adjust it.\n"
                    "If you want to create a new shipment, create a new sales order")
                    % r.name
                )

    @api.depends('order_line.is_freight')
    def _compute_is_freight(self):
        for record in self:
            record.is_freight = any(line.is_freight for line in record.order_line)

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        read_group = self.env['freight.booking'].read_group(
            [('sale_order_id', 'in', self.ids)],
            ['sale_order_id'],
            ['sale_order_id']
        )
        data = dict([(dict_data['sale_order_id'][0], dict_data['sale_order_id_count']) for dict_data in read_group])
        for order in self:
            order.booking_count = data.get(order.id, 0)

    @api.depends('shipment_ids', 'shipment_id')
    def _compute_shipment_count(self):
        for order in self:
            if order.shipment_id:
                order.shipment_count = 1
            else:
                order.shipment_count = len(order.shipment_ids)

    @api.depends('order_line.product_id.detailed_type')
    def _compute_visible_shipment(self):
        """ Users should be able to select a shipment_id on the SO if at least one SO line has a product with its detailed type
        configured as 'freight' """
        for order in self:
            order.visible_shipment = any(
                detailed_type == 'freight' for detailed_type in order.order_line.mapped('product_id.detailed_type') or
                order.shipment_ids
            )

    @api.depends('shipment_id', 'order_line.product_id')
    def _compute_mismatched_fields(self):
        """
        Check for mismatches between shipment fields and sales order data.
        This helps identify when shipment data has been manually changed and no longer
        matches what would be generated from the sales order.
        """
        for record in self:
            shipment = record.shipment_id
            if not shipment:
                record.mismatched_fields_warning = False
                continue

            freight_lines = record.order_line.filtered(lambda l: l.is_freight)
            mismatched_info = []

            mismatched_info.extend(self._check_multiple_leg_route_mismatch(shipment, freight_lines))

            if not shipment.multiple_leg_route and len(freight_lines) == 1:
                mismatched_info.extend(self._check_single_leg_shipment_mismatch(shipment, freight_lines[0]))

            elif shipment.multiple_leg_route:
                mismatched_info.extend(self._check_multi_leg_shipment_mismatch(shipment, freight_lines))

            record.mismatched_fields_warning = self._generate_mismatched_fields_warning(mismatched_info)

    @api.depends('shipment_id.transport_mode', 'shipment_ids.transport_mode',
             'shipment_id.ocean_shipping_method_id', 'shipment_ids.ocean_shipping_method_id',
             'shipment_id.air_shipping_method_id', 'shipment_ids.air_shipping_method_id',
             'shipment_id.land_shipping_method_id', 'shipment_ids.land_shipping_method_id',
             'shipment_id.direction', 'shipment_ids.direction')
    def _compute_transport_data(self):
        for order in self:
            shipment = order.shipment_id or order.shipment_ids[:1]
            if shipment:
                order.direction = shipment.direction
                order.transport_mode = shipment.transport_mode
                order.ocean_shipping_method_id = shipment.ocean_shipping_method_id
                order.air_shipping_method_id = shipment.air_shipping_method_id
                order.land_shipping_method_id = shipment.land_shipping_method_id
            else:
                order.direction = False
                order.transport_mode = False
                order.ocean_shipping_method_id = False
                order.air_shipping_method_id = False
                order.land_shipping_method_id = False

    def _check_multiple_leg_route_mismatch(self, shipment, freight_lines):
        """Check if multi-leg status matches."""
        mismatched_info = []
        is_multi_leg = len(freight_lines) > 1
        if shipment.multiple_leg_route != is_multi_leg:
            mismatched_info.append(_("Multiple Leg Route"))
        return mismatched_info

    def _check_single_leg_shipment_mismatch(self, shipment, line):
        """Check mismatches for single-leg shipments."""
        mismatched_info = []
        product = line.product_id
        route = product.route_id
        transport_mode = product.transport_mode

        checks = [
            (shipment.transport_mode, transport_mode,
                _("Transport Mode %s is not match") % shipment.name),
            (shipment.route_id, route,
                _("Route %s is not match") % shipment.name),
            (shipment.ocean_shipping_method_id, product.ocean_shipping_method_id,
                _("Ocean Shipping Method %s is not match") % shipment.name),
            (shipment.air_shipping_method_id, product.air_shipping_method_id,
                _("Air Shipping Method %s is not match") % shipment.name),
            (shipment.land_shipping_method_id, product.land_shipping_method_id,
                _("Land Shipping Method %s is not match") % shipment.name)
        ]

        mismatched_info.extend(
            mismatch_type for current, expected, mismatch_type in checks if current != expected
        )
        return mismatched_info

    def _check_multi_leg_shipment_mismatch(self, shipment, freight_lines):
        """Check mismatches for multi-leg shipments."""
        mismatched_info = []

        # Check number of routes
        if len(shipment.freight_route_ids) != len(freight_lines):
            mismatched_info.append(_("Number of Routes not match"))
        else:
            for line in freight_lines:
                mapping_route = shipment.freight_route_ids.filtered(
                    lambda r: r.route_id == line.product_id.route_id)[:1]

                if not mapping_route:
                    mismatched_info.append(_("sale line %s is not filled in any route") % line.name)
                else:
                    # Check transport mode and shipping methods
                    mismatched_info.extend(self._check_route_details(mapping_route, line))

        for route in shipment.freight_route_ids:
            if not route.sale_order_line_id:
                mismatched_info.append(_("Route %s is not mapped. Please add route and sync data.") % route.route_id.name)
        return mismatched_info

    def _check_route_details(self, mapping_route, line):
        """Check detailed route information."""
        mismatched_info = []
        product = line.product_id

        # Check transport mode and shipping methods
        checks = [
            (mapping_route.transport_mode, product.transport_mode,
                _("Transport Mode %s is not match") % mapping_route.name),
            (mapping_route.ocean_shipping_method_id, product.ocean_shipping_method_id,
                _("Ocean Shipping Method %s is not match") % mapping_route.name),
            (mapping_route.air_shipping_method_id, product.air_shipping_method_id,
                _("Air Shipping Method %s is not match") % mapping_route.name),
            (mapping_route.land_shipping_method_id, product.land_shipping_method_id,
                _("Land Shipping Method %s is not match") % mapping_route.name)
        ]

        mismatched_info.extend(
            mismatch_message for current, expected, mismatch_message in checks if current != expected
        )
        return mismatched_info

    def _generate_mismatched_fields_warning(self, mismatched_info):
        """Generate HTML warning message for mismatched fields."""
        if not mismatched_info:
            return False

        warning = '<div class="alert alert-warning" role="alert">'
        warning += _('<strong>Warning!</strong> The following fields do not match the sales order data:')
        warning += '<ul>'
        warning += ''.join(f'<li>{info}</li>' for info in mismatched_info)
        warning += '</ul>'
        warning += _('Consider updating these fields to match the sales order or update the sales order.')
        warning += '</div>'
        return warning

    def action_view_bookings(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_booking')
        action['domain'] = [('sale_order_id', 'in', self.ids)]
        context = {}
        context.update({
            'default_sale_order_id': self.id,
        })
        action['context'] = context
        return action

    def action_view_shipments(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_shipment')
        context = {}
        context.update({
            'default_sale_order_id': self[:1].id,
        })

        if self.shipment_id:
            form = self.env.ref('viin_freight_management.freight_shipment_form_view')
            action['views'] = [(form and form.id or False, 'form')]
            action['res_id'] = self.shipment_id.id
        elif len(self.shipment_ids) == 1:
            form = self.env.ref('viin_freight_management.freight_shipment_form_view')
            action['views'] = [(form and form.id or False, 'form')]
            action['res_id'] = self.shipment_ids.id
        elif len(self.shipment_ids) > 1:
            action['domain'] = [('id', 'in', self.shipment_ids.ids)]

        action['context'] = context
        return action

    def _action_cancel(self):
        """
        Extend the standard sale order cancellation process to cancel bookings if needed.
        This ensures that freight bookings are properly handled when a sales order is cancelled.
        """
        res = super(SaleOrder, self)._action_cancel()
        if self.env.user.has_group('viin_freight_management.group_freight_user'):
            self._activity_cancel_on_shipment()
        else:
            self.sudo()._activity_cancel_on_shipment()
        return res

    def _action_confirm(self):
        """
        Extend the standard sale order confirmation process to generate freight shipments.

        This method handles shipment creation and status updates based on user permissions
        and existing shipment records.
        """
        res = super(SaleOrder, self)._action_confirm()

        # Determine the appropriate context for writing shipment data
        safe_write_context = self.sudo() if not self.env.user.has_group('viin_freight_management.group_freight_user') else self

        # Handle shipment status and generation
        if safe_write_context.shipment_ids:
            safe_write_context.shipment_ids.write({
                'last_tracking_status': 'to_define',
            })
        elif safe_write_context.shipment_id:
            safe_write_context.shipment_id.write({
                'last_tracking_status': 'to_define',
            })
            safe_write_context.mapping_to_current_shipment()
        else:
            safe_write_context._generator_shipments()

        return res

    def _activity_cancel_on_shipment(self):
        """ If some SO are cancelled, we need to put an activity on their generated shipment. If sale lines of
            different sale orders impact different shipment, we only want one activity to be attached.
        """
        shipments = self.shipment_id or self.shipment_ids
        shipments.last_tracking_status = 'on_hold'

        for shipment in shipments:
            shipment._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=shipment.responsible_id.id or self.env.uid,
                views_or_xmlid='viin_freight_management.exception_sale_order_on_shipment_cancellation',
                render_context={
                    'sale_order': shipment.sale_order_id,
                    'shipments': shipment,
            })

    def _generator_shipments(self):
        """
        Automatically generate freight shipments based on freight lines in the sales order.
        - For multiple freight lines, create a multi-leg shipment with corresponding routes.
        - For a single freight line, create a direct shipment with all transport info embedded.
        Ensures that freight sales orders seamlessly transition into operational shipment records without manual intervention.
        """
        shipment_vals_list = []
        for order in self.filtered('is_freight'):
            freight_lines = order.order_line.filtered(lambda l: l.is_freight and l.need_prepare_freight)
            if not freight_lines:
                continue

            # Check if this is a multi-leg shipment
            is_multi_leg = len(freight_lines) > 1
            shipment_vals = {
                'sale_order_id': order.id,
                'sale_order_ids': [(6, 0, order.ids)],
                'multiple_leg_route': is_multi_leg,
            }

            if is_multi_leg:
                # Multi-leg: Create routes for each freight line
                route_commands = []
                for line in freight_lines:
                    route_vals = {
                        'name': line.product_id.name,
                    }
                    route_vals.update(line._prepare_route_vals())
                    route_commands.append((0, 0, route_vals))
                transport_mode_list = freight_lines.product_template_id.filtered(
                    lambda p: p.transport_mode
                ).mapped('transport_mode')
                if len(set(transport_mode_list)) > 1:
                    shipment_vals['transport_mode'] = 'multiple'
                else:
                    shipment_vals['transport_mode'] = transport_mode_list[0]
                shipment_vals['freight_route_ids'] = route_commands
            else:
                # Single route: Add transport info directly to shipment
                line = freight_lines[0]
                shipment_vals.update(line._prepare_shipment_vals())

            shipment_vals_list.append(shipment_vals)

        if shipment_vals_list:
            shipments = self.env['freight.shipment'].create(shipment_vals_list)
            return shipments
        return self.env['freight.shipment']

    def mapping_to_current_shipment(self):
        """
        Fill the current shipment with the sales order data.
        Only update fields that are not already filled in the shipment.
        """
        for order in self.filtered('is_freight'):
            freight_lines = order.order_line.filtered(lambda l: l.is_freight)
            shipment = order.shipment_id
            shipment.write({
                'sale_order_id': order.id,
                'sale_order_ids': [(6, 0, order.ids)],
                'sale_order_line_ids': [(6, 0, freight_lines.ids)],
            })

            if shipment.multiple_leg_route:
                freight_lines._mapping_to_route(shipment)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_transport_related(self):
        """The case here is to delete an order that has been confirmed and now not in "sale" state:
            - only allows to delete this order if it has no shipment, route or booking related.
        """
        for r in self:
            if r.company_id.prevent_unlink_sales_having_transport_related:
                if r.shipment_ids:
                    raise UserError(_("You may not be able to delete the sale order '%s' while it is still referred by "
                        "the shipment `%s`.\n"
                        "Please remove all the reference shipments first.")
                        % (r.name, r.shipment_ids[0].name)
                    )
                if r.booking_ids:
                    raise UserError(_("You may not be able to delete the sale order '%s' while it is still referred by "
                        "the booking `%s`.\n"
                        "Please remove all the reference bookings first.")
                        % (r.name, r.booking_ids[0].name)
                    )
                if r.freight_route_ids:
                    raise UserError(_("You may not be able to delete the sale order '%s' while it is still referred by "
                        "the route `%s`.\n"
                        "Please remove all the reference routes first.")
                        % (r.name, r.freight_route_ids[0].name)
                    )
