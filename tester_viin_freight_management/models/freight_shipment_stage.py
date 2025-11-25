from odoo import models, fields


class ShipmentStage(models.Model):
    _name = 'freight.shipment.stage'
    _description = 'Shipment Stage'
    _order = 'sequence, id'
    """Manage the stages of a shipment
    eg: Planning, Pickup, Pre-Carrier, On-Carrier, Main-Carrier, Post-Carrier, Delivered, etc.
    In there, there is a preiod when the main shipment route of the shipment is main-carrier.
    """

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description', translate=True)

    # Stage properties
    is_closed = fields.Boolean(
        string='Closed Stage',
        help="If checked, shipments in this stage are considered closed/completed.\n"
            "The stage will also be folded in kanban view when empty.")
    color = fields.Integer(string='Color Index')

    shipment_ids = fields.Many2many(
        'freight.shipment', 'freight_shipment_stage_rel', 'stage_id', 'shipment_id',
        string='Shipments'
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Stage name must be unique!')
    ]
