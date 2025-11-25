from odoo import models, fields


class ShipmentStatusTemplate(models.Model):
    _name = 'freight.shipment.status.template'
    _description = 'Shipment Status Template'

    name = fields.Char(string='Status', required=True, translate=True)
    active = fields.Boolean(string='Active', default=True)
