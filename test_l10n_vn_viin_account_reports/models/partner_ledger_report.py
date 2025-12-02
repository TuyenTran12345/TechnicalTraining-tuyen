from collections import defaultdict

from odoo import models, _


# pylint: disable=consider-merging-classes-inherited
class PartnerLedgerReport(models.Model):
    _inherit = 'account.report'

    def _get_customs_expanded_lines_partner_ledger(self, line, filter_options, columns):
        expanded_lines = super(PartnerLedgerReport, self)._get_customs_expanded_lines_partner_ledger(line, filter_options, columns)
        if self.env.company._filter_vietnam_coa():
            expanded_lines_strict_date = expanded_lines.copy()
            initial_line = expanded_lines_strict_date[0]
            if initial_line['id'].split('|')[-1] == 'initial-balance':
                expanded_lines_strict_date.pop(0)
            expanded_lines_incurrence = self._get_partner_ledger_incurrence(expanded_lines_strict_date, columns)
            expanded_lines += expanded_lines_incurrence
        return expanded_lines

    def _get_partner_ledger_incurrence(self, expanded_lines_strict_date, columns):
        """Calculates and returns a synthetic total balance line for a partner ledger."""
        line_totals = defaultdict(float)
        for line in expanded_lines_strict_date:
            for key in ('debit', 'credit'):
                line_totals[key] += line['columns'][key]['value'] or 0.0

        last_line = expanded_lines_strict_date and expanded_lines_strict_date[-1] or False
        if not last_line:
            return []
        parent_id = last_line['id'].split('|')[0]
        result = {
                'id': f'{parent_id}|total',
                'name': _('Total of incurrence'),
                'display_code': '',
                'level': last_line['level'],
                'parent_id': parent_id or 0,
                'class': f'account_report_level{last_line["level"]}',
                'unfoldable': False,
                'unfolded': False,
                'is_expanded_line': False,
                'visible': True,
                'groupby': '',
                'details_loaded': False,
                'columns': self._build_custom_line_columns(line_totals, columns),
            }
        result['columns']['balance']['formatted_value'] = ''
        return [result]
