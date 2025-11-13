from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shipment_id = fields.Many2one(
        'freight.shipment', string='Generated Shipment',
        compute='_compute_shipment', store=True, precompute=True, copy=False,
        help="Shipment generated from this sales order line, if applicable."
    )
    freight_route_id = fields.Many2one(
        'freight.route', string='Generated Route',
        compute='_compute_freight_route', store=True, precompute=True, copy=False,
        help="Specific transport route generated for this sales order line if using multi-leg shipping."
    )
    booking_ids = fields.Many2many(
        'freight.booking', string='Generated Booking',
        compute='_compute_booking_ids', store=True, precompute=True, copy=False,
        help="Booking associated with the shipment or freight route linked to this sales order line."
    )

    # technical fields
    is_freight = fields.Boolean(
        string='Is Freight', compute='_compute_is_freight',
        help="Technical field to identify if the product is a freight service (detailed_type = 'freight').")
    need_prepare_freight = fields.Boolean(
        string='Need Prepare Freight',
        compute='_compute_need_prepare_freight',
        help="Technical field indicating whether this line still needs to generate shipment or route based on its freight product.")

    @api.depends('product_id.detailed_type')
    def _compute_is_freight(self):
        for line in self:
            line.is_freight = line.product_id.detailed_type == 'freight'

    def _compute_need_prepare_freight(self):
        for line in self:
            line.need_prepare_freight = line.is_freight

    @api.depends('order_id.shipment_id')
    def _compute_shipment(self):
        for line in self:
            line.shipment_id = line.order_id.shipment_id

    @api.depends('shipment_id.freight_route_ids')
    def _compute_freight_route(self):
        for line in self:
            line.freight_route_id = line.shipment_id.freight_route_ids.filtered(
                lambda r: r.sale_order_line_id == line
            )[:1]

    @api.depends('freight_route_id.booking_ids', 'shipment_id.booking_ids')
    def _compute_booking_ids(self):
        for line in self:
            if line.freight_route_id.booking_ids:
                line.booking_ids = line.freight_route_id.booking_ids
            elif line.shipment_id.booking_ids:
                line.booking_ids = line.shipment_id.booking_ids
            else:
                line.booking_ids = False

    def _prepare_route_vals(self):
        """
        Prepare default values to create a freight route based on the product and vendor information.
        The route will inherit origin, destination, transport mode, and shipping method details from the linked freight product.
        """
        self.ensure_one()
        order = self.order_id
        product = self.product_id
        route = product.route_id
        return {
            'sale_order_line_id': self.id,
            'route_id': route.id,
            'sale_order_id': order.id,
            'service_type': route.service_type,
            'origin_id': route.departure_id.id,
            'destination_id': route.destination_id.id,
            'transport_mode': product.transport_mode,
            'ocean_shipping_method_id': product.ocean_shipping_method_id.id,
            'air_shipping_method_id': product.air_shipping_method_id.id,
            'land_shipping_method_id': product.land_shipping_method_id.id,
        }

    def _prepare_shipment_vals(self):
        """
        Prepare default values to create a shipment based on the product and vendor information.
        Shipment fields such as route, carrier, origin, and destination are populated from the linked freight product settings.
        """
        order = self.order_id
        product = self.product_id
        route = product.route_id
        shipment_vals = {
            'sale_order_line_id': self.id,
            'sale_order_id': order.id,
            'route_id': route.id,
            'service_type': route.service_type,
            'origin_id': route.departure_id.id,
            'destination_id': route.destination_id.id,
            'transport_mode': product.transport_mode,
            'ocean_shipping_method_id': product.ocean_shipping_method_id.id,
            'air_shipping_method_id': product.air_shipping_method_id.id,
            'land_shipping_method_id': product.land_shipping_method_id.id,
        }
        if route.service_type == 'port_to_port':
            shipment_vals.update({
                'port_of_loading_id': route.departure_id.id,
                'port_of_discharge_id': route.destination_id.id,
            })
        elif route.service_type == 'door_to_port':
            shipment_vals.update({
                'port_of_discharge_id': route.destination_id.id,
            })
        elif route.service_type == 'port_to_door':
            shipment_vals.update({
                'port_of_loading_id': route.departure_id.id,
            })
        return shipment_vals

    def _mapping_to_route(self, shipment):
        """
        Map the freight line to the route.
        param: shipment: single shipment record
        """
        for line in self:
            existing_route = shipment.freight_route_ids.filtered(
                lambda r: r.route_id == line.product_id.route_id and not r.sale_order_line_id)[:1]
            if existing_route:
                existing_route.write({'sale_order_line_id': line.id})

    @api.ondelete(at_uninstall=False)
    def _unlink_if_linked_shipment_or_route(self):
        """The case here is to delete order lines on a certain order
            - only allows to delete order lines if there has no shipment or route related.
        """
        for r in self:
            if r.company_id.prevent_unlink_sales_having_transport_related:
                if r.shipment_id:
                    raise UserError(_("You may not be able to remove the order line `%s` of the order `%s` "
                        "while it is still referred by the shipment `%s`.\n"
                        "Please remove all the referenced shipment first.")
                        % (r.name, r.order_id.name, r.shipment_id.name)
                    )
                if r.freight_route_id:
                    raise UserError(_("You may not be able to remove the order line `%s` of the order `%s` "
                        "while it is still referred by the route `%s`.\n"
                        "Please remove all the referenced route first.")
                        % (r.name, r.order_id.name, r.freight_route_id.name)
                    )
                if r.booking_ids:
                    raise UserError(_("You may not be able to remove the order line `%s` of the order `%s` "
                        "while it is still referred by the booking `%s`.\n"
                        "Please remove all the referenced booking first.")
                        % (r.name, r.order_id.name, r.booking_ids[:1].name)
                    )
