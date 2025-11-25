from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # technical field to check if the partner is a port.
    # Todo: Move me to to_geo_routes module when upgrade version 19.0
    is_port = fields.Boolean(string='Is Port', help="Check if the partner is a port")

    shipment_ids = fields.One2many('freight.shipment', 'customer_id', string='Shipments', groups="viin_freight_management.group_freight_user")
    shipment_count = fields.Integer(string='Shipments Count', compute='_compute_shipment_count', groups="viin_freight_management.group_freight_user")

    @api.constrains('is_port', 'country_id', 'ref')
    def _check_port_constraints(self):
        for record in self:
            if record.is_port:
                if not record.country_id:
                    raise UserError(_("You are creating a port but did not fill in the country. Please fill in the information at %s") % record.display_name)
                if not record.country_id.code:
                    raise UserError(_("The country %s does not have a code. Please fill in the code before creating the port %s") % (record.country_id.name, record.display_name))
                if not record.ref:
                    raise UserError(_("You are creating a port but did not fill in the port code. Please fill in the information at %s") % record.display_name)

    def _compute_display_name(self):
        super()._compute_display_name()
        for partner in self:
            if partner.is_port and partner.country_id:
                country_name = (partner.country_id.name or '').upper()
                country_code = (partner.country_id.code or '').upper()
                partner.display_name = "%s - %s (%s)" % (country_name, partner.ref or '', country_code)

    @api.depends('shipment_ids')
    def _compute_shipment_count(self):
        read_group = self.env['freight.shipment'].read_group(
            [('customer_id', 'in', self.ids)],
            ['customer_id'],
            ['customer_id']
        )
        mapped_data = dict([(data['customer_id'][0], data['customer_id_count']) for data in read_group])
        for partner in self:
            partner.shipment_count = mapped_data.get(partner.id, 0)

    def action_view_shipments(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.action_freight_shipment')
        context = {}
        context.update({
            'default_customer_id': self[:1].id,
        })
        if len(self.shipment_ids) == 1:
            form = self.env.ref('viin_freight_management.freight_shipment_form_view')
            action['views'] = [(form and form.id or False, 'form')]
            action['res_id'] = self.shipment_ids.id
        elif len(self.shipment_ids) > 1:
            action['domain'] = [('id', 'in', self.shipment_ids.ids)]
        action['context'] = context
        return action

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """Override:
            - When the user is a merchant, it will navigate to open a new view
        """
        res = super().get_view(view_id, view_type, **options)
        port_view = self.env.context.get('default_is_port', False)
        if port_view and view_type == 'form':
            port_view_id = self.sudo().env.ref("viin_freight_management.freight_port_form").id
            res = super().get_view(port_view_id, view_type, **options)
        return res
