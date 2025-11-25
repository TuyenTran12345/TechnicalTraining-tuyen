from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    shipment_ids = fields.One2many(
        'freight.shipment', 'analytic_account_id', string='Shipments')
    shipment_id = fields.Many2one(
        'freight.shipment', string='Shipment', compute='_compute_shipment_id', store=True,
        help="The shipment associated with this analytic account")

    @api.depends('shipment_ids')
    def _compute_shipment_id(self):
        for record in self:
            record.shipment_id = record.shipment_ids[:1]

    def _compute_display_name(self):
        """
        Override display name to display shipment suffix for analytic accounts
        when the related company has the custom_sale_account_analytic_suffix setting enabled.
        Example: SO0001 -> SO0001 - SHP0001
        """
        super()._compute_display_name()
        for record in self:
            shipment = record.shipment_id
            if not shipment:
                continue
            company = shipment.company_id or self.env.company
            if not company.custom_sale_account_analytic_suffix:
                continue
            if shipment.name not in record.display_name:
                record.display_name = f"{record.display_name} - {shipment.name}"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Override name_search to search by shipment name
        """
        if not self.env.company.custom_sale_account_analytic_suffix:
            return super().name_search(name, args, operator, limit)

        args = args or []
        domain = []
        if name:
            domain = ['|', ('shipment_id.name', '=ilike', '%' +
                            name + '%'), ('name', operator, name)]
        docs = self.search(domain + args, limit=limit)
        return [(doc.id, doc.display_name) for doc in docs]
