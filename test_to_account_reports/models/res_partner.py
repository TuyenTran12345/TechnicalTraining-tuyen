from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def open_partner_ledger(self):
        action = self.env["ir.actions.actions"]._for_xml_id("to_account_reports.partner_ledger_client_action")
        action['params'] = {
            'filterOptions': {'partner_ids': [self.id]},
        }
        return action
