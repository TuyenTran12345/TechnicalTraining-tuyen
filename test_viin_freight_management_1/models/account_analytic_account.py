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

    def name_get(self):
        """
        Override name_get to display shipment suffix for analytic accounts
        when the related company has the custom_sale_account_analytic_suffix setting enabled.
        Example: SO0001 -> SO0001 - SHP0001
        """
        result = []

        shipments_map = {}
        if self.ids:
            shipments = self.env['freight.shipment'].search([
                ('analytic_account_id', 'in', self.ids)
            ])
            shipments_map = {s.analytic_account_id.id: s for s in shipments}

        for record in self:
            name = record.name
            shipment = shipments_map.get(record.id)

            if shipment:
                company = shipment.company_id or self.env.company
                if company.custom_sale_account_analytic_suffix:
                    if shipment.name not in name:
                        name = f"{name} - {shipment.name}"

            result.append((record.id, name))
        return result

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
        return docs.name_get()
