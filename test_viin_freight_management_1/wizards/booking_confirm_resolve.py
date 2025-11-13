from odoo import api, fields, models, _


class BookingConfirmResolveWizard(models.TransientModel):
    _name = 'freight.booking.confirm.resolve.wizard'
    _description = 'Resolve carrier company at Booking confirm'
    _rec_name = 'booking_id'

    @api.model
    def default_get(self, fields_list):
        """Set smart defaults based on booking resolution requirement"""
        res = super().default_get(fields_list)

        if 'choice' in fields_list:
            booking_id = res.get('booking_id')
            booking = self.env['freight.booking'].browse(booking_id).exists()

            if booking:
                resolution_map = self._mapped_resolution_required()
                res['choice'] = resolution_map.get(booking.carrier_resolution_required, 'notify_stakeholders')

                if 'notification_subject' in fields_list:
                    subject_map = self._mapped_subject_resolution_required()
                    res['notification_subject'] = subject_map.get(
                        booking.carrier_resolution_required, _('Carrier Decision Required'))

                if 'stakeholder_user_ids' in fields_list:
                    stakeholders = booking.stakeholder_user_ids
                    if not stakeholders:
                        stakeholders = booking.stakeholder_user_ids
                    if not stakeholders:
                        stakeholders = self.env.user
                    res['stakeholder_user_ids'] = [(6, 0, stakeholders.ids)]

        return res

    @api.model
    def _mapped_subject_resolution_required(self):
        return {
            'notify_only': _('Notify stakeholders about carrier decision')
        }

    @api.model
    def _mapped_resolution_required(self):
        return {
            'notify_only': 'notify_stakeholders'
        }

    booking_id = fields.Many2one('freight.booking', string='Booking', required=True)
    choice = fields.Selection(selection='_get_available_choices', string='Choose Action', required=True)

    notification_message = fields.Text(string='Additional Message',
        help="Additional information to include in stakeholder notification")
    notification_subject = fields.Char(string='Notification Subject', default='Carrier Decision Required',
        help="Subject line for the notification activity")

    stakeholder_user_ids = fields.Many2many(
        'res.users', string='Notify Stakeholders', domain=[('share', '=', False)],
        help="Users who will receive notifications about this carrier issue")

    def _get_available_choices(self):
        """Return available choices for carrier resolution"""
        return [('notify_stakeholders', _('Notify stakeholders about carrier decision'))]

    def action_apply(self):
        self.ensure_one()
        booking = self.booking_id
        if not booking:
            return {"type": "ir.actions.act_window_close"}

        if self.choice == "notify_stakeholders":
            self._notify_stakeholders(booking)

        return booking.with_context(bypass_resolution_check=True).action_confirm()

    def _notify_stakeholders(self, booking):
        """Send email notifications using template via message_post"""
        stakeholders = self.stakeholder_user_ids
        if not stakeholders:
            return

        target_record = booking.shipment_id if booking.shipment_id else booking

        if booking.shipment_id:
            template = self.env.ref('viin_freight_management.email_template_shipment_carrier_resolution', raise_if_not_found=False)
        else:
            template = self.env.ref('viin_freight_management.email_template_carrier_resolution', raise_if_not_found=False)

        partner_ids = [user.partner_id.id for user in stakeholders]

        context_data = {
            'additional_message': self.notification_message,
            'notification_subject': self.notification_subject,
            'booking_name': booking.name,
            'carrier_name': booking.carrier_id.name if booking.carrier_id else 'N/A',
            'resolution_required': booking.carrier_resolution_required,
        }

        target_record.with_context(**context_data).message_post_with_template(
            template.id if template else False,
            subject=self.notification_subject or "Carrier Decision Required",
            partner_ids=partner_ids,
            auto_delete_message=False
        )
