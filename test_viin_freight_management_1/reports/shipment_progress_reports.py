from odoo import models, fields, tools


class ShipmentProgressReport(models.Model):
    _name = 'shipment.progress.report'
    _description = 'Shipment Progress'
    _auto = False

    shipment_id = fields.Many2one('freight.shipment', string='Shipment', readonly=True)
    freight_route_id = fields.Many2one('freight.route', string='Route Leg', readonly=True)
    route_id = fields.Many2one('route.route', string='Route', readonly=True)
    shipping_method_id = fields.Many2one('freight.shipping.method', string='Shipping Method', readonly=True)

    etd = fields.Date(string='ETD', readonly=True)
    eta = fields.Date(string='ETA', readonly=True)
    atd = fields.Date(string='ATD', readonly=True)
    ata = fields.Date(string='ATA', readonly=True)
    date = fields.Date(string='Created Date', readonly=True)

    transport_mode = fields.Selection([
        ('sea', 'Sea'),
        ('air', 'Air'),
        ('land', 'Land')
    ], string='Transport Mode', readonly=True)
    status = fields.Selection([
        ('inprogress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed')
    ], string='Status', readonly=True)
    delivery_status = fields.Selection([
        ('early', 'Early'),
        ('on_time', 'On Time'),
        ('late', 'Late'),
        ('in_transit', 'In Transit')
    ], string='Delivery Status', readonly=True)

    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    carrier_id = fields.Many2one('res.partner', string='Carrier', readonly=True)
    agent_id = fields.Many2one('res.partner', string='Agent', readonly=True)

    responsible_id = fields.Many2one('res.users', string='Responsible', readonly=True)
    sale_person_id = fields.Many2one('res.users', string='Sales Person', readonly=True)

    def _select(self):
        return """
            SELECT
                fr.id as id,
                fr.id as freight_route_id,
                fr.shipment_id,
                fr.route_id as route_id,
                fs.customer_id,
                fr.carrier_id,
                fr.agent_id,
                fs.responsible_id,
                so.user_id as sale_person_id,
                COALESCE(fr.ocean_shipping_method_id, fr.air_shipping_method_id, fr.land_shipping_method_id) as shipping_method_id,
                fr.transport_mode,
                fs.etd,
                fs.eta,
                fs.atd,
                fs.ata,
                fs.create_date::date as date,
                CASE
                    WHEN fss.is_closed IS TRUE THEN 'completed'
                    WHEN fs.last_tracking_status IN ('at_risk', 'off_track', 'on_hold') THEN 'delayed'
                    ELSE 'inprogress'
                END as status,
                fs.delivery_status
        """

    def _from(self):
        return "FROM freight_route fr"

    def _join(self):
        return """
            JOIN freight_shipment fs ON fr.shipment_id = fs.id
            LEFT JOIN sale_order so ON fs.sale_order_id = so.id
            LEFT JOIN freight_shipment_stage fss ON fs.current_stage_id = fss.id
        """

    def _query(self):
        return f"""
            {self._select()}
            {self._from()}
            {self._join()}
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._query()}
            )
        """)
