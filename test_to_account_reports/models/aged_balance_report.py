from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.tools import get_lang


# pylint: disable=consider-merging-classes-inherited
class AgedBalanceReport(models.Model):
    _inherit = 'account.report'

    def _get_customs_lines_aged_receivable(self, filter_options, columns):
        return self._get_customs_lines_aged_balance(filter_options, columns, 'asset_receivable')

    def _get_customs_lines_aged_payable(self, filter_options, columns):
        return self._get_customs_lines_aged_balance(filter_options, columns, 'liability_payable')

    def _get_customs_lines_aged_balance(self, filter_options, columns, account_type):
        """
        As mentioned in _get_customs_lines method. If report want to generate custom line then it must be define a method with format
        '_get_customs_lines_%s' % self.custom_line_python_function_suffix

        With this report, we have 2 custom methods: _get_customs_lines_aged_receivable and _get_customs_lines_aged_payable
        and they call to this method to generate custom line based on account_type
        """
        date_to = filter_options['current_date']['date_to']
        periods = self._build_aged_periods(date_to)
        period_table_cte = self._build_aged_period_table_cte(periods)
        period_query_select = self._build_period_query_select(periods, account_type)

        domain = [('account_id.account_type', '=', account_type), ('partner_id', '!=', False)]
        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': date_to}
            })
        table, where_clauses, where_params = self._get_sql(filter_options, 'from_beginning', extend_domain=domain)

        if self.pool['res.partner'].name.translate:
            lang = self.env.user.lang or get_lang(self.env).code
            partner_name = f"COALESCE(partner.display_name->>'{lang}', partner.display_name->>'en_US')"
        else:
            partner_name = 'partner.display_name'

        self.env['account.move.line'].flush_model()
        query = """
            {period_table_cte}
            SELECT
                account_move_line.partner_id AS partner_id,
                {partner_name} AS partner_name,
                {period_query_select}
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
            LEFT JOIN LATERAL (
                SELECT
                    SUM(amount) AS amount,
                    debit_move_id
                FROM account_partial_reconcile
                WHERE max_date <= '{date_to}'
                GROUP BY debit_move_id
            ) partial_reconcile_debit ON partial_reconcile_debit.debit_move_id = account_move_line.id
            LEFT JOIN LATERAL (
                SELECT
                    SUM(amount) AS amount,
                    credit_move_id
                FROM account_partial_reconcile
                WHERE max_date <= '{date_to}'
                GROUP BY credit_move_id
            ) partial_reconcile_credit ON partial_reconcile_credit.credit_move_id = account_move_line.id
            JOIN period_table_cte
                ON (
                    period_table_cte.date_from IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table_cte.date_from))
                AND (
                    period_table_cte.date_to IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table_cte.date_to)
                )
            WHERE {where_clauses}
            GROUP BY
                account_move_line.partner_id,
                period_table_cte.period_key,
                {partner_name}
            ORDER BY partner_name
        """.format(
            period_table_cte=period_table_cte,
            partner_name=partner_name,
            period_query_select=period_query_select,
            table=table,
            currency_table=currency_table,
            date_to=date_to,
            where_clauses=where_clauses,
            )

        self._cr.execute(query, where_params)
        results = self._cr.dictfetchall()
        return self._build_aged_lines(results, columns)

    def _build_aged_periods(self, date_to):
        periods = {}
        date_to = fields.Date.from_string(date_to)

        periods.update({0: {
            'date_from': False,
            'date_to': fields.Date.to_string(date_to)
            }})
        periods.update({1: {
            'name': '1-30',
            'date_from': fields.Date.to_string(date_to - relativedelta(days=1)),
            'date_to': fields.Date.to_string(date_to - relativedelta(days=30))
            }})
        periods.update({2: {
            'name': '31-60',
            'date_from': fields.Date.to_string(date_to - relativedelta(days=31)),
            'date_to': fields.Date.to_string(date_to - relativedelta(days=60))
            }})
        periods.update({3: {
            'name': '61-90',
            'date_from': fields.Date.to_string(date_to - relativedelta(days=61)),
            'date_to': fields.Date.to_string(date_to - relativedelta(days=90))
            }})
        periods.update({4: {
            'name': '91-120',
            'date_from': fields.Date.to_string(date_to - relativedelta(days=91)),
            'date_to': fields.Date.to_string(date_to - relativedelta(days=120))
            }})
        periods.update({5: {
            'name': 'older',
            'date_from': fields.Date.to_string(date_to - relativedelta(days=121)),
            'date_to': False
            }})

        return periods

    def _build_aged_period_table_cte(self, periods):
        """
        We need a common table expression with columns are period_key, date_from, date_to and row corresponding to each period
        """
        period_table = []
        for key, value in periods.items():
            date_from = value['date_from'] if value['date_from'] else None
            date_to = value['date_to'] if value['date_to'] else None
            if not date_from:
                period_table.append("(%s, %s, '%s')" % (key, date_from, date_to))
            elif not date_to:
                period_table.append("(%s, '%s', %s)" % (key, date_from, date_to))
            else:
                period_table.append("(%s, '%s', '%s')" % (key, date_from, date_to))

        period_table = '(VALUES %s)' % ','.join(period_table)
        period_table = period_table.replace('None', 'NULL')

        return 'WITH period_table_cte(period_key, date_from, date_to) AS (%s)' % period_table

    def _build_period_query_select(self, periods, account_type):
        """
        Each period we need build to corresponding column in the select with column name format:
        period{pertiod_key}
        """
        period_query_select = []
        sign = 1 if account_type == 'asset_receivable' else -1
        for key in periods:
            sql_select = """
                CASE WHEN period_table_cte.period_key = {key} THEN (
                        SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision))
                        - COALESCE(SUM(ROUND(partial_reconcile_debit.amount * currency_table.rate, currency_table.precision)), 0)
                        + COALESCE(SUM(ROUND(partial_reconcile_credit.amount * currency_table.rate, currency_table.precision)), 0)
                    ) * {sign} ELSE 0 END AS period{key}
            """.format(key=key, sign=sign)
            period_query_select.append(sql_select)

        return ','.join(period_query_select)

    def _build_aged_lines(self, results, columns):
        """
        From the list of results that have been queried, we need to build the rows and their corresponding period columns.
        However, these result may duplicate partner data while we want each partner to be a line with its corresponding columns.

        So, we need build result_dict to ensure not duplicate partner

        Finally, we need insert total line at the first line
        """
        lines = []
        result_dict = {}
        for res in results:
            result_dict.setdefault(res['partner_id'], {
                    'partner_id': 0,
                    'partner_name': '',
                    'period0': 0,
                    'period1': 0,
                    'period2': 0,
                    'period3': 0,
                    'period4': 0,
                    'period5': 0,
                    'total': 0,
                })

        for key, values in result_dict.items():
            for res in results:
                if res['partner_id'] == key:
                    values['partner_id'] = res['partner_id']
                    values['partner_name'] = res['partner_name']
                    values['period0'] += res['period0']
                    values['period1'] += res['period1']
                    values['period2'] += res['period2']
                    values['period3'] += res['period3']
                    values['period4'] += res['period4']
                    values['period5'] += res['period5']
                    values['total'] += res['period0'] + res['period1'] + res['period2'] + res['period3'] + res['period4'] + res['period5']

        for val in result_dict.values():
            if val['total']:
                lines.append({
                    'id': '~res.partner~%s' % val['partner_id'],
                    'name': val['partner_name'],
                    'display_code': '',
                    'level': 3,
                    'parent_id': '~res.partner~0',
                    'class': 'account_report_level3',
                    'unfoldable': True,
                    'unfolded': False,
                    'is_expanded_line': False,
                    'is_customs_line': True,
                    'visible': True,
                    'groupby': 'id',
                    'columns': self._build_custom_line_columns(val, columns),
                })

        lines.insert(0, {
            'id': '~res.partner~total',
            'name': _('Total'),
            'display_code': '',
            'level': 3,
            'parent_id': 0,
            'class': 'account_report_level3 fw-bolder',
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': True,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_aged_total_line_columns(result_dict, columns)
        })

        return lines

    def _build_aged_total_line_columns(self, result_dict, columns):
        """
        Total line need have a total columns and this method will build this total column
        """
        columns_dict = {}
        for column in columns:
            figure_type = column['figure_type']
            blank_if_zero = column['blank_if_zero']

            if column['key'].startswith('period') or column['key'] == 'total':
                value = sum(val[column['key']] for val in result_dict.values())
                formatted_value = self._format_value(value, figure_type, blank_if_zero)
                column_class = self._get_line_column_css_class(value)
            else:
                value = 0.0
                formatted_value = ''
                column_class = ''

            columns_dict.update({
                column['key']: {
                    'value': value,
                    'formatted_value': formatted_value,
                    'unfoldable': False,
                    'expression_id': 0,
                    'auditable': False,
                    'column_class': column_class,
                    'figure_type': figure_type,
                    'blank_if_zero': blank_if_zero,
                }
            })

        return columns_dict

    def _get_customs_expanded_lines_aged_receivable(self, line, filter_options, columns):
        return self._get_customs_expanded_lines_aged_balance(line, filter_options, columns, 'asset_receivable')

    def _get_customs_expanded_lines_aged_payable(self, line, filter_options, columns):
        return self._get_customs_expanded_lines_aged_balance(line, filter_options, columns, 'liability_payable')

    def _get_customs_expanded_lines_aged_balance(self, line, filter_options, columns, account_type):
        """
        As mentioned in _get_customs_expanded_lines method, this method to generate customs expanded lines of receivable or payable
        """
        lines = []
        date_to = filter_options['current_date']['date_to']
        periods = self._build_aged_periods(date_to)
        period_table_cte = self._build_aged_period_table_cte(periods)
        period_query_select = self._build_period_query_select(periods, account_type)
        sign = 1 if account_type == 'asset_receivable' else -1

        domain = [('account_id.account_type', '=', account_type)]
        split_line_ids = line['id'].split('~')
        if split_line_ids:
            domain += [('partner_id', '=', int(split_line_ids[2]))]

        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': date_to}
            })
        table, where_clauses, where_params = self._get_sql(filter_options, 'strict_range', extend_domain=domain)

        self.env['account.move.line'].flush_model()
        query = """
            {period_table_cte}
            SELECT
                account_move_line.id AS id,
                account_move_line.move_id AS move_id,
                account_move_line.move_name AS name,
                move.invoice_date AS invoice_date,
                (
                    SUM(account_move_line.amount_currency)
                    - COALESCE(SUM(partial_reconcile_debit.debit_amount_currency), 0)
                    + COALESCE(SUM(partial_reconcile_credit.credit_amount_currency), 0)
                ) * {sign} AS amount_currency,
                account_move_line.currency_id,
                account.code AS account_name,
                COALESCE(account_move_line.date_maturity, account_move_line.date) AS due_date,
                {period_query_select}
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN account_account account ON account.id = account_move_line.account_id
            LEFT JOIN account_move move ON move.id = account_move_line.move_id
            LEFT JOIN LATERAL (
                SELECT
                    SUM(amount) AS amount,
                    SUM(debit_amount_currency) AS debit_amount_currency,
                    debit_move_id
                FROM account_partial_reconcile
                WHERE max_date <= '{date_to}'
                GROUP BY debit_move_id
            ) partial_reconcile_debit ON partial_reconcile_debit.debit_move_id = account_move_line.id
            LEFT JOIN LATERAL (
                SELECT
                    SUM(amount) AS amount,
                    SUM(credit_amount_currency) AS credit_amount_currency,
                    credit_move_id
                FROM account_partial_reconcile
                WHERE max_date <= '{date_to}'
                GROUP BY credit_move_id
            ) partial_reconcile_credit ON partial_reconcile_credit.credit_move_id = account_move_line.id
            JOIN period_table_cte
                ON (
                    period_table_cte.date_from IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table_cte.date_from))
                AND (
                    period_table_cte.date_to IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table_cte.date_to)
                )
            WHERE {where_clauses}
            GROUP BY
                account_move_line.id,
                period_table_cte.period_key,
                move.invoice_date,
                account.code
        """.format(
            period_table_cte=period_table_cte,
            sign=sign,
            period_query_select=period_query_select,
            table=table,
            currency_table=currency_table,
            date_to=date_to,
            where_clauses=where_clauses,
            )

        self._cr.execute(query, where_params)
        results = self._cr.dictfetchall()
        for res in results:
            total = res['period0'] + res['period1'] + res['period2'] + res['period3'] + res['period4'] + res['period5']
            if total:
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
