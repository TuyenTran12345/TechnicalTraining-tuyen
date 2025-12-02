from datetime import timedelta
import copy

from odoo import fields, models, _
from odoo.tools import get_lang
from odoo.osv import expression


# pylint: disable=consider-merging-classes-inherited
class PartnerLedgerReport(models.Model):
    _inherit = 'account.report'

    def _get_customs_lines_partner_ledger(self, filter_options, columns):
        """
        This report similar to General Ledger, so see general_ledger_report.py for more details
        """
        lines = []

        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': filter_options['current_date']['date_to']}
            })
        table, where_clauses, where_params = self._get_sql(filter_options, 'from_beginning')

        if self.pool['res.partner'].name.translate:
            lang = self.env.user.lang or get_lang(self.env).code
            partner_name = f"COALESCE(partner.display_name->>'{lang}', partner.display_name->>'en_US')"
        else:
            partner_name = 'partner.display_name'

        self.env['account.move.line'].flush_model()
        query = """
            SELECT
                account_move_line.partner_id,
                {partner_name} AS partner_name,
                SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)) AS debit,
                SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)) AS credit,
                SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
            WHERE {where_clauses}
            GROUP BY account_move_line.partner_id, partner.display_name
            ORDER BY partner_name
        """.format(
            partner_name=partner_name,
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )

        self._cr.execute(query, where_params)
        line_total_value = {total: 0.0 for total in ['debit', 'credit', 'balance']}
        result = self._cr.dictfetchall()
        for res in result:
            if res['partner_id']:
                lines.append(self._prepare_customs_line_partner_ledger_vals(filter_options, res, columns))
                for key in ['debit', 'credit', 'balance']:
                    line_total_value[key] += res[key]

        # Add total line
        lines.append({
            'id': '~res.partner~total',
            'name': _('Total'),
            'display_code': '',
            'level': 3,
            'parent_id': 0,
            'class': 'account_report_level3 fw-bolder',
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': False,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_custom_line_columns(line_total_value, columns),
        })
        return lines

    def _prepare_customs_line_partner_ledger_vals(self, filter_options, result, columns):
        res = {
            'id': '~res.partner~%s' % result['partner_id'],
            'name': result['partner_name'],
            'display_code': '',
            'level': 3,
            'parent_id': 0,
            'class': 'account_report_level3',
            'unfoldable': True,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': True,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_custom_line_columns(result, columns),
        }

        action_domain = [('partner_id', '=', result['partner_id'])]
        action_domain = expression.AND([action_domain, self._build_domain_from_options(filter_options, 'strict_range')])
        action_dict = {
            'name': _("Journal Items"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'list',
            'views': [(False, 'list')],
            'domain': action_domain,
        }

        res['action_dict'] = action_dict

        return res

    def _get_customs_expanded_lines_partner_ledger(self, line, filter_options, columns):
        expanded_lines = []
        extend_domain = []

        split_line_ids = line['id'].split('~')
        if split_line_ids:
            extend_domain = [('partner_id', '=', int(split_line_ids[2]))]

        expanded_lines += self._get_partner_ledger_initial_balance(line, filter_options, extend_domain, columns)
        expanded_lines += self._get_partner_ledger_strict_date(line, filter_options, extend_domain, columns)

        balance = 0.0
        for expanded_line in expanded_lines:
            balance += expanded_line['columns']['debit']['value'] - expanded_line['columns']['credit']['value']
            expanded_line['columns']['balance']['value'] = balance
            figure_type = expanded_line['columns']['balance']['figure_type']
            blank_if_zero = expanded_line['columns']['balance']['blank_if_zero']
            expanded_line['columns']['balance']['formatted_value'] = self._format_value(balance, figure_type, blank_if_zero)
            column_class = self._get_line_column_css_class(balance)
            expanded_line['columns']['balance']['column_class'] = column_class

        return expanded_lines

    def _get_partner_ledger_initial_balance(self, line, filter_options, extend_domain, columns):
        if not line:
            return []

        lines = []
        domain = []
        domain += extend_domain

        new_options = self._get_partner_ledger_initial_balance_options(filter_options)
        if new_options.get('include_initial_balance', False):
            domain += [('account_id.include_initial_balance', '=', True)]

        table, where_clauses, where_params = self._get_sql(new_options, 'normal', extend_domain=domain)
        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': new_options['current_date']['date_to']}
        })
        query = """
            SELECT
                COALESCE(SUM(account_move_line.amount_currency), 0.0) AS amount_currency,
                COALESCE(SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)), 0.0) AS debit,
                COALESCE(SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)), 0.0) AS credit,
                COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            WHERE {where_clauses}
        """.format(
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )

        self._cr.execute(query, where_params)
        result = self._cr.dictfetchone()
        lines.append({
            'id': '%s|initial-balance' % line['id'],
            'name': _('Initial Balance'),
            'display_code': '',
            'level': line['level'] + 1,
            'parent_id': line['id'] or 0,
            'class': 'account_report_level%s' % (line['level'] + 1),
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'visible': True,
            'groupby': '',
            'details_loaded': False,
            'columns': self._build_custom_line_columns(result, columns),
        })

        return lines

    def _get_partner_ledger_strict_date(self, line, filter_options, extend_domain, columns):
        lines = []
        table, where_clauses, where_params = self._get_sql(filter_options, 'strict_range', extend_domain=extend_domain)
        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': filter_options['current_date']['date_to']}
        })
        self.env['account.move.line'].flush_model()
        query = """
            SELECT
                account_move_line.id AS id,
                account_move_line.date AS name,
                journal.code AS journal_code,
                account.code AS account_code,
                account_move_line.move_name AS ref,
                move.invoice_date AS invoice_date,
                account_move_line.date_maturity,
                account_move_line.matching_number,
                account_move_line.move_id AS move_id,
                account_move_line.currency_id,
                COALESCE(account_move_line.amount_currency, 0.0) AS amount_currency,
                ROUND(account_move_line.debit * currency_table.rate, currency_table.precision) AS debit,
                ROUND(account_move_line.credit * currency_table.rate, currency_table.precision) AS credit,
                ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN account_journal journal ON journal.id = account_move_line.journal_id
            LEFT JOIN account_account account ON account.id = account_move_line.account_id
            LEFT JOIN account_move move ON move.id = account_move_line.move_id
            WHERE {where_clauses}
            ORDER BY account_move_line.date
        """.format(
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )

        self._cr.execute(query, where_params)
        result = self._cr.dictfetchall()
        for res in result:
            action_dict = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(self.env.ref('account.view_move_form').id, 'form')],
                'res_model': 'account.move',
                'res_id': res['move_id'],
                'view_id': self.env.ref('account.view_move_form').id,
                'context': self._context,
            }

            lines.append({
                'id': '%s|~account.move.line~%s' % (line['id'], res['id']),
                'name': res['name'],
                'display_code': '',
                'level': line['level'] + 1,
                'parent_id': line['id'] or 0,
                'class': 'account_report_level%s' % (line['level'] + 1),
                'unfoldable': False,
                'unfolded': False,
                'is_expanded_line': True,
                'visible': True,
                'groupby': '',
                'details_loaded': False,
                'columns': self._build_custom_line_columns(res, columns),
                'action_dict': action_dict,
            })

        return lines

    def _get_partner_ledger_initial_balance_options(self, filter_options):
        new_options = copy.deepcopy(filter_options)
        current_date = new_options.get('current_date', False)
        if current_date:
            date_to = fields.Date.from_string(current_date['date_from']) - timedelta(days=1)
            new_options['current_date']['date_from'] = None
            new_options['current_date']['date_to'] = fields.Date.to_string(date_to)

        return new_options
