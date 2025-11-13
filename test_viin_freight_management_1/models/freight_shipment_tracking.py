from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

TRACKING_FIELD_LIST = [
    'transport_mode', 'service_type',
    'carrier_id', 'agent_id', 'consignee_id', 'notify_party_id',
    'ocean_shipping_method_id', 'air_shipping_method_id', 'land_shipping_method_id',
    'vessel_name', 'vessel_voyage_number', 'air_name', 'air_voyage_number', 'truck_name', 'driver_id',
    'route_id', 'origin_id', 'port_of_loading_id', 'port_of_discharge_id', 'destination_id',
    'etd', 'eta', 'cutoff', 'atd', 'ata',
]


class ShipmentTracking(models.Model):
    _name = 'freight.shipment.tracking'
    _description = 'Shipment Tracking'
    _inherit = ['freight.transport.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'event_time desc, id desc'

    def default_get(self, fields_list):
        """Copy logic from project update
        """
        result = super().default_get(fields_list)
        shipment_id = self.env.context.get('default_shipment_id', False)
        shipment = self.env['freight.shipment'].browse(shipment_id).exists()
        if shipment:
            result['status'] = shipment.last_tracking_status if shipment.last_tracking_status != 'to_define' else 'on_track'
        return result

    title_template_id = fields.Many2one('freight.shipment.status.template', string='Title Template', required=True, help="Select a title template for this tracking update")

    # Event Information
    event_time = fields.Datetime(
        string='Event Time', required=True, default=fields.Datetime.now,
        help="When this tracking event occurred"
    )
    location = fields.Char(string='Location', help="Current location of the shipment")
    details = fields.Html(string='Details', help="Detailed information about this tracking update")
    status = fields.Selection(selection=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold')
    ], required=True, string='Update Status for Shipment',
        help="You can update the status of the shipment at this tracking point")

    # Stage Management
    stage_id = fields.Many2one(
        'freight.shipment.stage', string='Stage',
        domain="[('shipment_ids', 'in', shipment_id)]",
        help="The stage of the shipment at this tracking point"
    )

    # Portal & Notification Settings
    is_published = fields.Boolean(
        string='Published on Portal', default=True,
        help="Make this update visible on the customer portal"
    )
    notify_to_partner_ids = fields.Many2many(
        'res.partner', string='Notify To',
        help="Partners who will receive email notifications about this tracking update"
    )

    # Related Info (for easy access and filtering)
    shipment_id = fields.Many2one('freight.shipment', string='Shipment', required=True)

    # technical field
    should_send_notification = fields.Boolean(string='Should Send Notification', compute='_compute_should_send_notification')
    need_update_shipment_plan = fields.Boolean(
        string='Need update shipment planning',
        help="If this tracking update affects the original transportation plan, you can enable this field to "
            "update the shipment information directly here."
    )

    # --- Fields to update shipment ---
    multiple_leg_route = fields.Boolean(related='shipment_id.multiple_leg_route')
    freight_route_id = fields.Many2one('freight.route', string='Freight Route',
        domain="[('shipment_id', '=', shipment_id)]",
        help="Select a freight route in this shipment if want to update this route infomation. "
            "Otherwise, the tracking information will be updated to the shipment directly.")

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, "[%s] %s" % (r.title_template_id.name, r.event_time.strftime('%Y-%m-%d %H:%M:%S'))))
        return result

    @api.constrains('event_time')
    def _check_event_time(self):
        """Ensure tracking events are not in the future"""
        for record in self:
            if record.event_time > fields.Datetime.now():
                raise ValidationError(_('Event time cannot be in the future!'))

    @api.depends('notify_to_partner_ids', 'is_published')
    def _compute_should_send_notification(self):
        """Compute should_send_notification based on notify_to_partner_ids and is_published"""
        for record in self:
            record.should_send_notification = bool(record.notify_to_partner_ids and record.is_published)

    @api.onchange('need_update_shipment_plan', 'freight_route_id')
    def _onchange_source_id(self):
        """
        When changing shipment, need_update_shipment_plan, or freight_route_id,
        auto-fill tracking fields from the corresponding shipment or route.
        """
        if self.need_update_shipment_plan:
            source_record = self.freight_route_id if self.multiple_leg_route else self.shipment_id
            if source_record:
                update_vals = self._copy_values_from_source_to_tracking(source_record)
                if update_vals:
                    self.update(update_vals)
        if self.freight_route_id:
            self.notify_to_partner_ids = self.freight_route_id.third_party_ids
            self.status = self.shipment_id.last_tracking_status if self.shipment_id.last_tracking_status != 'to_define' else 'on_track'

    def _get_portal_url(self):
        """Get the portal URL for this tracking record"""
        return '/my/shipment/%s' % (self.shipment_id.id)

    def _send_tracking_notification(self):
        """
        Send a tracking update email notification to all assigned partners.
        Process:
            - Collect partner emails.
            - Format email using a predefined template.
            - Send a single email to all partners.
        Raises:
            Logs a warning if the email template is missing.
        """
        self.ensure_one()
        template = self.env.ref('viin_freight_management.email_template_shipment_tracking')

        if not template:
            _logger.warning("Email template for shipment tracking not found")
            return

        # Get company email info
        company = self.company_id or self.env.company
        email_from = f'"{company.name}" <{company.email or self.env.user.email}>'

        # Get valid partners and their emails
        notify_partners = self.notify_to_partner_ids.filtered('email')
        if not notify_partners:
            return

        partner_emails = notify_partners.mapped('email_formatted')
        # Convert partner names to list of strings and handle formatting
        partner_names = [str(name) for name in notify_partners.mapped('name')]
        if len(partner_names) > 1:
            partner_name = f"{', '.join(map(str, partner_names[:-1]))} {_('and')} {partner_names[-1]}"
        else:
            partner_name = partner_names[0]

        # Prepare common email context
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        tracking_url = '{}{}'.format(base_url, self._get_portal_url())

        # Send one email to all partners
        template.with_context(
            tracking_url=tracking_url,
            partner_name=partner_name  # Use formatted partner names
        ).send_mail(
            self.id,
            force_send=True,
            email_values={
                'email_from': email_from,
                'email_to': ','.join(partner_emails),
                'auto_delete': False,
            }
        )

    def _create_notification_action(self, title, message, notification_type, next_action=None):
        """Helper method to create notification action with consistent structure

        :param title: Notification title
        :param message: Notification message
        :param notification_type: Type of notification (success, warning, danger)
        :param next_action: Optional next action to execute after notification
        :return: Action dict for client notification
        """
        params = {
            'title': title,
            'message': message,
            'type': notification_type,
        }
        if next_action:
            params['next'] = next_action

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': params,
        }

    def action_send_update_email(self):
        """Manual action to send/resend tracking update email"""
        self.ensure_one()

        # Check if the tracking has recipients
        if not self.should_send_notification:
            return self._create_notification_action(
                title=_('Warning'),
                message=_('No notification recipients selected. Please add recipients first.'),
                notification_type='warning'
            )

        # Send the email notification
        try:
            self._send_tracking_notification()
            return self._create_notification_action(
                title=_('Success'),
                message=_('Tracking update email sent to %s') % (
                    ', '.join(self.notify_to_partner_ids.mapped('name'))
                ),
                notification_type='success',
                next_action={
                    'type': 'ir.actions.act_window_close',
                }
            )

        except Exception as e:
            return self._create_notification_action(
                title=_('Error'),
                message=_('Failed to send email: %s') % str(e),
                notification_type='danger'
            )

    def write(self, vals):
        """
        Override write method to synchronize tracking fields back to the shipment or route
        if 'need_update_shipment_plan' is enabled.
        """
        res = super().write(vals)
        for rec in self:
            source_record = rec.freight_route_id if rec.freight_route_id else rec.shipment_id
            if rec.need_update_shipment_plan and source_record:
                update_vals = rec.with_context(tracking_copy_collect_values=True)._copy_tracking_fields()
                if update_vals:
                    source_record.write(update_vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to handle automatic synchronization immediately after creating a tracking record,
        if 'need_update_shipment_plan' is enabled.
        """
        records = super().create(vals_list)
        for rec in records:
            source_record = rec.freight_route_id if rec.multiple_leg_route and rec.freight_route_id else rec.shipment_id
            if source_record:
                if rec.need_update_shipment_plan:
                    update_vals = rec.with_context(tracking_copy_collect_values=True)._copy_tracking_fields()
                    if update_vals:
                        source_record.write(update_vals)
            rec.shipment_id.write({'last_tracking_id': rec})
            if rec.freight_route_id:
                rec.freight_route_id.write({'last_tracking_id': rec})
        return records

    def _copy_tracking_fields(self):
        """
        Helper method to copy field values from a source record (shipment or route)
        to the current tracking record, based on TRACKING_FIELD_MAPPING.

        Returns:
            dict: A dictionary of values to update (used in create/write), or None (used in onchange).
        """
        update_vals = {}
        for tracking_field in TRACKING_FIELD_LIST:
            if tracking_field in ['route_id', 'carrier_id', 'agent_id', 'consignee_id', 'notify_party_id']:
                value = getattr(self, tracking_field).id
            else:
                value = getattr(self, tracking_field)
            if self._fields.get(tracking_field):
                if self.env.context.get('tracking_copy_collect_values', False):
                    # If collecting values for write/create
                    update_vals[tracking_field] = value
        if self.env.context.get('tracking_copy_collect_values', False):
            return update_vals
        return None

    def _copy_values_from_source_to_tracking(self, source_record):
        """
        Helper method to copy field values FROM a source record (shipment or route)
        TO the current tracking record, based on TRACKING_FIELD_MAPPING.
        Used specifically for onchange events.

        Returns:
            dict: A dictionary of values to update in the tracking record.
        """
        update_vals = {}
        for tracking_field in TRACKING_FIELD_LIST:
            if hasattr(source_record, tracking_field):
                value = getattr(source_record, tracking_field)
                if self._fields.get(tracking_field):
                    update_vals[tracking_field] = value
        return update_vals
