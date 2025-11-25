from odoo import fields, models, api


class RouteRoute(models.Model):
    _inherit = 'route.route'

    service_type = fields.Selection([
        ('door_to_door', 'Door to Door'),
        ('port_to_port', 'Port to Port'),
        ('door_to_port', 'Door to Port'),
        ('port_to_door', 'Port to Door'),
    ], string='Service Type', compute='_compute_service_type', store=True, default='door_to_door',
        help="Type of service provided by this route (Door to Door, Port to Port, Door to Port, or Port to Door).")
    product_ids = fields.One2many(
        'product.product', 'route_id', string='Products', index=True,
        help="Product templates associated with this route."
    )

    @api.depends('waypoint_ids.address_id.is_port')
    def _compute_service_type(self):
        for route in self:
            if route.waypoint_ids:
                first_point_type = "port" if route.waypoint_ids[0].address_id.is_port else "door"
                last_point_type = "port" if route.waypoint_ids[-1].address_id.is_port else "door"
                route.service_type = f"{first_point_type}_to_{last_point_type}"
            else:
                route.service_type = 'door_to_door'
