from odoo import models, api, _
from odoo.exceptions import UserError


class AccountCommonReport(models.TransientModel):
    _inherit = 'account.common.report'

    @api.model
    def _validate_date_from_and_date_to(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("The Date From cannot be greater than the Date To"))
        return True

    def _build_contexts(self, data):
        result = super(AccountCommonReport, self)._build_contexts(data)
        date_from = result.get('date_from', False)
        date_to = result.get('date_to', False)
        if date_from and date_to:
            self._validate_date_from_and_date_to(date_from, date_to)
        return result
