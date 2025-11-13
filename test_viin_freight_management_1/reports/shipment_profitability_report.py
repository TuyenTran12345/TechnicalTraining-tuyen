from odoo import models, fields, tools


class ShipmentProfitabilityReport(models.Model):
    _name = 'shipment.profitability.report'
    _description = 'Shipment Profitability'
    _auto = False

    # Shipment
    shipment_id = fields.Many2one('freight.shipment', string='Shipment', readonly=True)
    route_id = fields.Many2one('route.route', string='Route', readonly=True)
    date = fields.Date(string='Date', readonly=True)

    shipping_method = fields.Char(string='Loading Method', readonly=True)
    status = fields.Selection([
        ('inprogress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
    ], string='Status', readonly=True)
    transport_mode = fields.Selection([
        ('sea', 'Sea'),
        ('air', 'Air'),
        ('land', 'Land'),
        ('multiple', 'Multi-Modal')
    ], string='Transport Mode', readonly=True)
    delivery_status = fields.Selection([
        ('early', 'Early'),
        ('on_time', 'On Time'),
        ('late', 'Late'),
        ('in_transit', 'In Transit')
    ], string='Delivery Status', readonly=True)

    # Customer
    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    shipper_id = fields.Many2one('res.partner', string='Shipper', readonly=True)
    consignee_id = fields.Many2one('res.partner', string='Consignee', readonly=True)

    # Internal User
    sale_person_id = fields.Many2one('res.users', string='Sale Person', readonly=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', readonly=True)

    # Analytic
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    # Financial
    price_subtotal = fields.Monetary(string='Revenue (Untaxed)', readonly=True, group_operator='sum')
    price_total = fields.Monetary(string='Total (Incl. Tax)', readonly=True, group_operator='sum')
    untaxed_amount_invoiced = fields.Monetary(string='UnTaxed Amount Invoiced', readonly=True, group_operator='sum')
    untaxed_amount_to_invoice = fields.Monetary(string='UnTaxed Amount To Invoice', readonly=True, group_operator='sum')
    cost = fields.Monetary(string='Cost', readonly=True, group_operator='sum')
    profit = fields.Monetary(string='Profit', readonly=True, group_operator='sum')
    profit_margin = fields.Float(string='Profit Margin (%)', readonly=True, group_operator='avg')

    # -------------------------------
    # SQL Parts
    # -------------------------------

    def _with(self):
        return """
            WITH revenue AS (
                SELECT sol.shipment_id,
                    SUM(CASE WHEN sol.invoice_status = 'no' THEN 0 ELSE sol.price_subtotal END) as revenue,
                    SUM(CASE WHEN sol.invoice_status = 'no' THEN 0 ELSE sol.price_total END) as price_total,
                    SUM(sol.untaxed_amount_invoiced) as untaxed_invoiced,
                    SUM(sol.untaxed_amount_to_invoice) as untaxed_to_invoice
                FROM sale_order_line sol
                WHERE sol.shipment_id IS NOT NULL
                GROUP BY sol.shipment_id
            ),
            cost AS (
                SELECT account_id, -SUM(amount) as cost
                FROM account_analytic_line
                WHERE amount < 0
                GROUP BY account_id
            )
        """

    def _select(self):
        return """
            SELECT
                fs.id as id,
                fs.id as shipment_id,
                fs.route_id,
                fs.customer_id,
                fs.shipper_id,
                fs.consignee_id,
                fs.responsible_id,
                so.user_id as sale_person_id,
                fs.analytic_account_id,
                fs.create_date::date as date,
                fs.shipping_method,
                CASE
                    WHEN fss.is_closed IS TRUE THEN 'completed'
                    WHEN fs.last_tracking_status IN ('at_risk', 'off_track', 'on_hold') THEN 'delayed'
                    ELSE 'inprogress'
                END as status,
                fs.transport_mode,
                fs.delivery_status,
                so.currency_id as currency_id,

                COALESCE(r.revenue, 0) as price_subtotal,
                COALESCE(r.price_total, 0) as price_total,
                COALESCE(r.untaxed_invoiced, 0) as untaxed_amount_invoiced,
                COALESCE(r.untaxed_to_invoice, 0) as untaxed_amount_to_invoice,

                COALESCE(c.cost, 0) as cost,
                COALESCE(r.revenue, 0) - COALESCE(c.cost, 0) as profit,
                CASE
                    WHEN COALESCE(r.revenue, 0) = 0 THEN 0
                    ELSE ROUND(((COALESCE(r.revenue, 0) - COALESCE(c.cost, 0)) / r.revenue) * 100, 2)
                END as profit_margin
        """

    def _from(self):
        return """
            FROM freight_shipment fs
            LEFT JOIN sale_order so ON fs.sale_order_id = so.id
            LEFT JOIN freight_shipment_stage fss ON fs.current_stage_id = fss.id
            LEFT JOIN revenue r ON r.shipment_id = fs.id
            LEFT JOIN cost c ON c.account_id = fs.analytic_account_id
        """

    def _group_by(self):
        return """
            GROUP BY
                fs.id,
                fs.route_id,
                fs.customer_id,
                fs.shipper_id,
                fs.consignee_id,
                fs.responsible_id,
                so.user_id,
                fs.analytic_account_id,
                fs.create_date,
                fss.is_closed,
                fs.shipping_method,
                fs.transport_mode,
                fs.delivery_status,
                fs.last_tracking_status,
                so.currency_id,
                r.revenue,
                r.price_total,
                r.untaxed_invoiced,
                r.untaxed_to_invoice,
                c.cost
        """

    def _query(self):
        return f"""
            {self._with()}
            {self._select()}
            {self._from()}
            {self._group_by()}
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._query()}
            )
        """)
