from odoo import models


class AccountReportColumn(models.Model):
    _inherit = 'account.report.column'

    def _prepare_column_vals_list(self, column_header):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_column_vals(column_header))

        return vals_list

    def _prepare_column_vals(self, column_header):
        """
        We have 3 types of column:
        - Origin Column: these columns are defined in account report. This case has not 'column_key'
        - Percent Column: these columns are created if there is a comparison for only one column. It's column key is 'percent'
        - Other Column: these columns has format 'comparison_%s', 'initial_balance_%s', 'ending_balance_%s'
        with comparison or initial_balance is column key of column header
        """
        self.ensure_one()
        column_key = column_header.get('key', '')
        if not column_key:
            column_key = self.expression_label
        elif column_key == 'percent':
            column_key = 'percent'
        else:
            column_key = '%s_%s' % (column_key, self.expression_label)
        return {
            'name': self.name,
            'key': column_key,
            'figure_type': self.figure_type,
            'blank_if_zero': self.blank_if_zero,
        }
