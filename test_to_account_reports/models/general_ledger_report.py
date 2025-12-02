from odoo import models, _
from odoo.tools import get_lang
from odoo.osv import expression


# pylint: disable=consider-merging-classes-inherited
class GeneralLedgerReport(models.Model):
    _inherit = 'account.report'

    def _get_customs_lines_general_ledger(self, filter_options, columns):
        """
        As mentioned in _get_customs_lines method, this method generate lines for General Ledger
        """
        lines = []
        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': filter_options['current_date']['date_to']}
            })
        queries = []
        params = []
        get_sql = []
        # Get data for initial balance and strict range
        table, where_clauses, where_params = self._get_sql(
            filter_options,
            'from_beginning',
            extend_domain=[('account_id.include_initial_balance', '=', True)]
        )
        get_sql.append((table, where_clauses, where_params))
        # Get data for initial balance and strict range with out account include initial balance
        table, where_clauses, where_params = self._get_sql(
            filter_options,
            'strict_range',
            extend_domain=[('account_id.include_initial_balance', '=', False)]
        )
        get_sql.append((table, where_clauses, where_params))
        self.env['account.move.line'].flush_model()

        for table, where_clauses, where_params in get_sql:
            queries.append(f"""
                SELECT
                    account_move_line.account_id,
                    account.code,
                    SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)) AS debit,
                    SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)) AS credit,
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                FROM {table}
                LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN account_account account ON account.id = account_move_line.account_id
                WHERE {where_clauses}
                GROUP BY account_move_line.account_id, account.code
                HAVING
                    SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)) <> 0 OR
                    SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)) <> 0 OR
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) <> 0
            """)
            params += [*where_params]

        self._cr.execute(' UNION ALL '.join(queries), params)
        result = self._cr.dictfetchall()
        # TODO: select account code and account name with multi lang and replace to browse(account_id)
        account_ids = [r['account_id'] for r in result]
        for res in sorted(result, key=lambda r: r['code']):
            account = self.env['account.account'].browse(res['account_id']).with_prefetch(prefetch_ids=account_ids)
            lines.append(self._prepare_customs_line_general_ledger_vals(filter_options, res, account, columns))

        return lines

    def _prepare_customs_line_general_ledger_vals(self, filter_options, result, account, columns, is_unaffected_earnings=False):
        """
        Hook method to prepare general ledger line
        """
        res = {
            'id': '~account.account~%s' % result['account_id'],
            'name': account.display_name,
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
            'is_unaffected_earnings': is_unaffected_earnings
        }

        action_domain = [('account_id', '=', result['account_id'])]
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

    def _get_customs_expanded_lines_general_ledger(self, line, filter_options, columns):
        """
        As mentioned in _get_customs_expanded_lines method, this method generate general ledger expanded line when user click on any line
        General Ledger expanded line contain 2 parts:
        - Initial Balance information
        - Account Move Line in period
        """
        expanded_lines = []
        extend_domain = []

        split_line_ids = line['id'].split('~')
        if split_line_ids:
            extend_domain = [('account_id', '=', int(split_line_ids[2]))]

        expanded_lines += self._get_general_ledger_initial_balance(
            line,
            filter_options,
            expression.AND([extend_domain, [('account_id.include_initial_balance', '=', True)]]),
            columns
        )
        expanded_lines += self._get_general_ledger_strict_date(
            line,
            filter_options,
            extend_domain,
            columns
        )

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

    def _get_general_ledger_initial_balance(self, line, filter_options, extend_domain, columns):
        """
        As mentioned in _get_customs_expanded_lines_general_ledger, this method generate initial balance line
        """
        if not line:
            return []

        lines = []

        new_options = self._get_initial_balance_option(filter_options)

        table, where_clauses, where_params = self._get_sql(new_options, 'normal', extend_domain=extend_domain)
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

    def _get_general_ledger_strict_date(self, line, filter_options, extend_domain, columns):
        """
        As mentioned in _get_customs_expanded_lines_general_ledger, this method generate lines in period
        """
        lines = []
        table, where_clauses, where_params = self._get_sql(filter_options, 'strict_range', extend_domain=extend_domain)
        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': filter_options['current_date']['date_to']}
        })

        if self.pool['res.partner'].name.translate:
            lang = self.env.user.lang or get_lang(self.env).code
            partner_name = f"COALESCE(partner.display_name->>'{lang}', partner.display_name->>'en_US')"
        else:
            partner_name = 'partner.display_name'

        query = """
            SELECT
                account_move_line.id AS id,
                account_move_line.move_id AS move_id,
                account_move_line.move_name AS name,
                MAX(account_move_line.date) AS date,
                account_move_line.name AS communication,
                {partner_name} AS partner_name,
                account_move_line.currency_id,
                COALESCE(account_move_line.amount_currency, 0.0) AS amount_currency,
                ROUND(account_move_line.debit * currency_table.rate, currency_table.precision) AS debit,
                ROUND(account_move_line.credit * currency_table.rate, currency_table.precision) AS credit,
                ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
            WHERE {where_clauses}
            GROUP BY
                account_move_line.id,
                account_move_line.partner_id,
                currency_table.rate,
                currency_table.precision,
                partner.display_name
        """.format(
            partner_name=partner_name,
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
