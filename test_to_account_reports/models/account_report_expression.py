from ast import literal_eval
import copy
import re
from itertools import groupby
from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import expr_eval
from odoo.osv import expression


class AccountReportExpression(models.Model):
    _inherit = 'account.report.expression'

    use_amount_residual = fields.Boolean(string='Use Amount Residual',
        help="If checked, this expression will be get amount_residual of move line instead of balance."
            " In some case, we need amount_residual not balance, for example: "
            " 'Advance Payments received from customers' of Cash Flow Statement")
    use_reconcile = fields.Boolean(string='Use Reconcile', default=False,
        help="If checked, this expression will be get amount of Reconcile instead matched of move line."
            " In some case, we need reconcile amount not balance, for example: "
            " 'Revenue of fixed assets and other long-term assets' of Cash Flow Statement")
    reconcile_domain = fields.Char(string='Reconcile Domain',
        help="This field is used for domain engine. It will be added to domain of report line before calculate.")

    def _cal_expression_values(self, filter_options, date_scope=None, comparison=False):
        """
        As mentioned in the _get_lines method of the account.report model. This method will calculate the value of each expression
        and return a result of the following:
        [
            {'line_code': 'BA', 'expression_name': 'debit', 'value': 5},
            {'line_code': 'BA', 'expression_name': 'credit', 'value': 2},
            {'line_code': 'BA', 'expression_name': 'balance', 'value': 3},
            {'line_code': 'REC', 'expression_name': 'debit', 'value': 7},
            {'line_code': 'REC', 'expression_name': 'credit', 'value': 6},
            {'line_code': 'REC', 'expression_name': 'balance', 'value': 1},
            ...
        ]
        """
        res = []
        for r in self:
            res.append(r._prepare_expression_vals(filter_options, date_scope=date_scope, comparison=comparison))

        res = self._cal_expression_engine_aggregation(filter_options, res)

        return res

    def _prepare_expression_vals(self, filter_options, date_scope=None, comparison=False):
        self.ensure_one()
        value = 0.0
        formatted_value = ''
        unfoldable = False
        auditable = False
        exp_method = '_cal_expression_engine_%s' % self.engine

        # Aggregation engine do not calculate in here. They will be calculated after all other engine calculated
        if self.engine == 'aggregation':
            value = self.formula
            formatted_value = value  # we have no need format in this case
        elif hasattr(self, exp_method):
            results = getattr(self, exp_method)(filter_options, date_scope=date_scope)
            value = results['value']
            value = self._handle_subformula(value)
            formatted_value = self._format_value(value)
            unfoldable = results.get('has_line_details', False)

        if value is not None and self.engine in ('tax_tags', 'domain', 'account_codes'):
            auditable = self.auditable

        res = {
            'line_id': self.report_line_id.id,
            'line_code': self.report_line_id.code,
            'expression_id': self.id,
            'expression_name': self.label,
            'engine': self.engine,
            'expression_key': 'comparison_%s' % self.label if comparison else self.label,
            'value': value,
            # value used to calculation for other expressions
            # So we need formatted_value key to display it in report
            'formatted_value': formatted_value,
            'unfoldable': unfoldable,
            # TODO: support auditable with 'external' or 'aggregation' engine in the future
            'auditable': auditable,
            'green_on_positive': self.green_on_positive,
            'figure_type': self.figure_type
        }
        return res

    def _cal_expression_engine_domain(self, filter_options, date_scope=None):
        """
        Return value of expression with domain engine

        Even though balance already stores based on company's currency. However, in a multi-company environment
        sometimes users want to see consolidated reports. In case, we need to convert this balance to the company's base currency in env.
        Because each company may have a different base currency, the balance now needs to be converted to the company's base currency in env
        """
        self.ensure_one()
        domain = literal_eval(self.formula) if self.formula else []
        if not date_scope:
            date_scope = self.date_scope
        duration_term_domain = self.report_line_id._prepare_duration_term_domain(filter_options['current_date']['date_to'])
        domain = expression.AND([domain, duration_term_domain])
        table, where_clauses, where_params = self.env['account.report']._get_sql(filter_options, date_scope, extend_domain=domain)

        self.env['account.move.line'].flush_model()

        if self.use_reconcile:
            query = f"""
                SELECT account_move_line.id
                FROM {table}
                WHERE {where_clauses}
            """
            self._cr.execute(query, where_params)
            query_result = self._cr.dictfetchall()
            move_line_ids = [res['id'] for res in query_result]
            move_lines = self.env['account.move.line'].browse(move_line_ids).with_prefetch(prefetch_ids=move_line_ids)
            partial_reconcile_vals = self._get_partial_reconcile_value(move_lines, filter_options, date_scope=date_scope)
            if self.use_amount_residual:
                value = sum([element['amount_residual'] for element in partial_reconcile_vals])
            else:
                value = sum([element['amount'] for element in partial_reconcile_vals])
            count_line_details = len(partial_reconcile_vals)
            return {
                'value': value or 0.0,
                'has_line_details': count_line_details > 0
            }

        else:
            currency_table = self.env['res.currency']._get_query_currency_table({
                'multi_company': True, 'date': {'date_to': filter_options['current_date']['date_to']}
                })
            column = 'amount_residual' if self.use_amount_residual else 'balance'
            group_by_select = self.report_line_id.groupby and ', %s' % self.report_line_id.groupby or ''
            group_by = self.report_line_id.groupby and 'GROUP BY %s' % self.report_line_id.groupby or ''
            query = """
                SELECT
                    COALESCE(SUM(account_move_line.{column} * currency_table.rate), 0.0) AS sum,
                    COUNT(account_move_line.id)
                    {group_by_select}
                FROM {table}
                JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
                WHERE {where_clauses}
                {group_by}
            """.format(
                column=column,
                group_by_select=group_by_select,
                table=table,
                currency_table=currency_table,
                where_clauses=where_clauses,
                group_by=group_by
                )
            self._cr.execute(query, where_params)
            query_result = self._cr.dictfetchall()
            results = []
            for res in query_result:
                if self.subformula:
                    if 'sum_if_pos' in self.subformula:
                        if res['sum'] > 0:
                            results.append(res)
                    elif 'sum_if_neg' in self.subformula:
                        if res['sum'] < 0:
                            results.append(res)
                    else:
                        results.append(res)
                else:
                    results.append(res)

            value = sum(res['sum'] for res in results)
            has_line_details = len(results) > 0

        return {
            'value': value or 0.0,
            'has_line_details': has_line_details}

    def _cal_expression_engine_tax_tags(self, filter_options, date_scope=None):
        """
        return value of expression with tax_tags engine
        """
        self.ensure_one()
        tags = self._get_matching_tags()
        if not tags:
            return {
                'value': 0.0,
                'has_line_details': False
            }
        if not date_scope:
            date_scope = self.date_scope
        domain = self.report_line_id._prepare_duration_term_domain(filter_options['current_date']['date_to'])
        table, where_clauses, where_params = self.env['account.report']._get_sql(filter_options, date_scope, extend_domain=domain)

        self.env['account.move.line'].flush_model()

        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': filter_options['current_date']['date_to']}
            })

        query = """
            SELECT
                SUM(ROUND(COALESCE(account_move_line.balance, 0) * currency_table.rate, currency_table.precision)
                    * CASE WHEN acc_tag.tax_negate THEN -1 ELSE 1 END
                    * CASE WHEN account_move_line.tax_tag_invert THEN -1 ELSE 1 END
                ) AS sum,
                COUNT(account_move_line.id)
            FROM {table}
            JOIN account_account_tag_account_move_line_rel aml_tag ON aml_tag.account_move_line_id = account_move_line.id
            JOIN account_account_tag acc_tag ON aml_tag.account_account_tag_id = acc_tag.id AND acc_tag.id IN %s
            JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            WHERE {where_clauses}
        """.format(
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )

        self._cr.execute(query, [tuple(tags.ids)] + where_params)
        result = self._cr.dictfetchone()

        return {
            'value': result['sum'] or 0.0,
            'has_line_details': result['count'] > 0}

    def _cal_expression_engine_aggregation(self, filter_options, exp_res):

        def update_expression_value(origin_formula, formula_item, new_exp_item):
            """
            origin_formula: CF200.balance = CF200_01.balance + CF200_02.balance - CF200_03.balance
            formula_item: CF200_01.balance
            new_exp_item: CF200_01_01.balance + CF200_01_02.balance  or 10 + 20
            return CF200.balance = (CF200_01_01.balance + CF200_01_02.balance) + CF200_02.balance - CF200_03.balance
            or     CF200.balance = (10 + 20) + CF200_02.balance - CF200_03.balance
            """
            return re.sub(r"(^|(?<=[ ()+/*-]))%s((?=[ ()+/*-])|$)" % re.escape(formula_item), '(%s)' % new_exp_item, origin_formula)

        def split_formula(origin_formula):
            """
            origin_formula: CF200_01.balance + CF200_02.balance - CF200_03.balance
            return [CF200_01.balance, CF200_02.balance, CF200_03.balance]
            """
            new_formula = []
            for item in re.split(r'[+-]|[ ()/*]', origin_formula.replace(" ", "")):
                try:
                    float(item)
                except ValueError:
                    if item:
                        new_formula.append(item)
            return new_formula

        def eval_formula(formula):
            try:
                value = expr_eval(formula)
            except ZeroDivisionError:
                value = 0.0
            return value

        def load_expression_value(aggregation_exp):
            """
            line_code: CF200
            expression_name: balance
            return: with type string
            find the value of the expression and calculate the value of the CF200.balance expression based on the exp_res_dict data
            str: (10 + 20) + 70 - 0
            """
            line_code = aggregation_exp['line_code']
            expression_name = aggregation_exp['expression_name']
            row = exp_res_dict['%s.%s' % (line_code, expression_name)]
            if not row:
                return None
            engine = row['engine']
            expression_value = row['value']

            if engine != 'aggregation' or (engine == 'aggregation' and isinstance(expression_value, float)):
                return str(expression_value)
            else:
                expression_formula = expression_value
                exp_value = bool(expression_formula) and expression_formula or str(0.0)
                new_formula = split_formula(expression_formula)
                for formula_item in new_formula:
                    try:
                        new_exp_res_dict = exp_res_dict[formula_item]
                    except KeyError:
                        exp_record = self.browse(aggregation_exp['expression_id'])
                        code, expression = formula_item.split('.')
                        if exp_record.subformula and exp_record.subformula == 'cross_report':
                            # in this case, the current expression is calculated using the value of an expression belonging to another report
                            # while the current data only has data from expressions in the current report, a KeyError error will be encountered
                            # now we will handle it by:
                            #    - find the report line with code = item
                            #    - get report of the report line
                            #    - call back the '_cal_expression_values' of the report
                            #    - if not found, raise error
                            #    - if found, get the value in the return result of the '_cal_expression_values' function above
                            code, expression = formula_item.split('.')
                            cross_report_line = self.env['account.report.line'].search([('code', '=', code)], limit=1)
                            if not cross_report_line:
                                raise ValidationError(_("Cannot find report line has code '%s'") % formula_item)

                            date_scope = exp_record.date_scope or None
                            cross_exp_res = cross_report_line.report_id.line_ids.expression_ids._cal_expression_values(filter_options, date_scope=date_scope)
                            cross_exp_res_dict = {}
                            for exp in cross_exp_res:
                                cross_exp_res_dict.setdefault('%s.%s' % (exp['line_code'], exp['expression_name']), {})
                                cross_exp_res_dict['%s.%s' % (exp['line_code'], exp['expression_name'])].update(exp)
                            new_exp_res_dict = cross_exp_res_dict[formula_item]
                            # after calculating, you need to update exp_res_dict so you don't have to recalculate
                            exp_res_dict.update({formula_item: cross_exp_res_dict[formula_item]})
                        else:
                            raise ValidationError(_("Cannot find expression for '%s'") % formula_item)
                    sub_expression_value = load_expression_value(new_exp_res_dict)
                    if sub_expression_value is not None:
                        exp_value = update_expression_value(
                            origin_formula=exp_value,
                            formula_item=formula_item,
                            new_exp_item=sub_expression_value
                        )
                return exp_value

        # define data with key: ('line_code', 'expression_name')
        exp_res_dict = {'%s.%s' % (exp['line_code'], exp['expression_name']): exp for exp in exp_res}

        for aggregation_exp in exp_res:
            aggregation_exp['calculated_formula'] = load_expression_value(aggregation_exp)

        for aggregation_exp in exp_res:
            aggregation_exp['value'] = eval_formula(aggregation_exp['calculated_formula'])

        for exp in exp_res:
            value = exp['value']
            exp_record = self.browse(exp['expression_id'])
            formatted_value = value
            if exp_record.exists():
                formatted_value = exp_record._format_value(value)
            exp['value'] = value
            exp['formatted_value'] = formatted_value

        return exp_res

    def _cal_expression_engine_custom(self, filter_options, date_scope=None):
        """
        This method handle the expression with Custom Python Function engine.
        NOTE:
        - This function must belong model account.report
        - This function must has params are filter_options, date_scope,...
        - This function must be start with '_report_custom'
        """
        if not self.formula:
            return None
        if not self.formula.startswith('_report_custom'):
            raise ValidationError(_("The custom python function %s must be start with '_report_custom'") % self.formula)

        return getattr(self.env['account.report'], self.formula)(filter_options, date_scope=date_scope)

    def _handle_subformula(self, value):
        """
        The value of the expression after being calculated needs to be processed with subformula: -sum, sum_if_pos, sum_if_neg,...
        """
        sign = 1
        if self.subformula and self.subformula.strip()[0] == '-':
            sign = -1

        return value * sign

    def _format_value(self, value):
        """
        Value need to format before show in report.

        Note: column of the report also have some of the same options as expression.
        Therefore some options maybe not set on expressions but set on column.
        For example: figure_type, blank_if_zero,...
        """
        self.ensure_one()
        report_columns = self.report_line_id.report_id.column_ids.filtered(lambda c: c.expression_label == self.label)

        figure_type = self.figure_type
        if not figure_type and report_columns:
            figure_type = report_columns[0].figure_type

        blank_if_zero = self.blank_if_zero
        if not blank_if_zero and report_columns:
            blank_if_zero = report_columns[0].blank_if_zero

        return self.env['account.report']._format_value(value, figure_type, blank_if_zero)

    def _build_domain_from_options(self, filter_options, date_scope=None):
        """
        Build domain from filter options and date scope.
        """
        domain = []
        mode = 'in_range' if filter_options.get('use_filter_date_range', False) else 'at_time'
        if current_date := filter_options.get('current_date', False):
            date_from = current_date.get('date_from', False)
            date_to = current_date.get('date_to', False)
            if date_to:
                if mode == 'at_time':
                    date_from = None

                if date_scope == 'from_fiscalyear':
                    date_from = self.env.company.compute_fiscalyear_dates(fields.Date.from_string(date_to))['date_from']
                    date_from = date_from.strftime('%Y-%m-%d')

                elif date_scope == 'to_beginning_of_period':
                    date_to = fields.Date.from_string(date_from or date_to) - relativedelta(days=1)
                    date_to = date_to.strftime('%Y-%m-%d')
                    date_from = None

                elif date_scope == 'to_beginning_of_fiscalyear':
                    date_to = self.env.company.compute_fiscalyear_dates(fields.Date.from_string(date_to))['date_from'] - relativedelta(days=1)
                    date_to = date_to.strftime('%Y-%m-%d')
                    date_from = None

                elif date_scope == 'from_beginning':
                    date_from = None

                if date_from:
                    if mode == 'at_time':
                        date_from = None
                    else:
                        domain += [('max_date', '>=', date_from)]

                domain += [('max_date', '<=', date_to)]
        return domain

    def _get_partial_values(self, amls, filter_options, date_scope=None):
        """
        Retrieve reconciled partial values for given account move lines within a specified date range.
        :param amls: Account move lines to consider for reconciliation.
        :type amls: Recordset of account.move.line

        :param filter_options: Filter options containing date range.
        :type filter_options: dict

        :param date_scope: Date scope for reconciliation (optional).
        :type date_scope: str

        :return: A dictionary containing reconciled partial values with debit move id, credit move id, and amount_partial.
        :rtype: dict
        """
        # Filter account move lines to consider only those that can be reconciled.
        amls = amls.filtered('account_id.reconcile')
        if not amls:
            return {}

        # Flush model to ensure up-to-date data.
        self.env['account.partial.reconcile'].flush_model()

        # Get domain
        domain = self._build_domain_from_options(filter_options, date_scope)

        query = self.env['account.partial.reconcile']._where_calc(domain)

        _, where_clause, where_clause_args = query.get_sql()

        # SQL queries to retrieve reconciled partial values.
        select_query = f"""
            SELECT
                account_partial_reconcile.debit_move_id AS debit_move_id,
                account_partial_reconcile.credit_move_id AS credit_move_id,
                sum(account_partial_reconcile.amount) AS amount_partial
            FROM account_partial_reconcile
            LEFT JOIN account_move_line AS aml_debit ON aml_debit.id = account_partial_reconcile.debit_move_id
            WHERE
                aml_debit.id IN %s AND {where_clause}
            GROUP BY
                account_partial_reconcile.debit_move_id, account_partial_reconcile.credit_move_id
            UNION ALL
            SELECT
                account_partial_reconcile.debit_move_id AS debit_move_id,
                account_partial_reconcile.credit_move_id AS credit_move_id,
                -sum(account_partial_reconcile.amount) AS amount_partial
            FROM account_partial_reconcile
            LEFT JOIN account_move_line AS aml_credit ON aml_credit.id = account_partial_reconcile.credit_move_id
            WHERE
                aml_credit.id IN %s AND {where_clause}
            GROUP BY
                account_partial_reconcile.debit_move_id, account_partial_reconcile.credit_move_id
        """

        # Parameters for SQL queries.
        params = [
            tuple(amls.ids),
            *where_clause_args
        ] * 2

        # Execute SQL queries and fetch results.
        self._cr.execute(select_query, params)
        return self._cr.dictfetchall()

    def _get_partial_reconcile_value(self, move_lines, filter_options, date_scope=None):
        if not move_lines:
            return []
        result = []

        # In case it's already in cash, you don't have to go get it during reconciliation
        move_line_asset_cash = move_lines.filtered(lambda line: line.account_id.account_type == 'asset_cash')
        result.extend([{'id': aml.id, 'amount': 0.0} for aml in move_line_asset_cash])

        # In case other
        amls_to_matched = (move_lines - move_line_asset_cash).filtered('account_id.reconcile')
        partials_values = self._get_partial_values(amls_to_matched, filter_options, date_scope)

        # Separate matched debit and credit lines
        matched_debit_aml_ids = set(partial['debit_move_id'] for partial in partials_values)
        matched_credit_aml_ids = set(partial['credit_move_id'] for partial in partials_values)

        # Process prepayments
        prepayment_ids = set()
        for aml in amls_to_matched:
            if (aml.is_debit() and aml.id not in matched_debit_aml_ids) or (aml.is_credit() and aml.id not in matched_credit_aml_ids):
                prepayment_ids.add(aml.id)
        prepayment_move_lines = self.env['account.move.line'].browse(prepayment_ids)
        result.extend([{'id': aml.id, 'amount': 0.0} for aml in prepayment_move_lines])

        # Update data with time conditions
        amls_to_matched = amls_to_matched - prepayment_move_lines
        ctp_aml_ids = []

        partials_values_copy = copy.deepcopy(partials_values)
        partials_values = []

        for aml in amls_to_matched:
            if aml.is_debit() and aml.id in matched_debit_aml_ids:
                for partial in partials_values_copy[:]:
                    if aml.id == partial['debit_move_id']:
                        partials_values.append(partial)
                        ctp_aml_ids.append(partial['credit_move_id'])
                        partials_values_copy.remove(partial)
            elif aml.is_credit() and aml.id in matched_credit_aml_ids:
                for partial in partials_values_copy[:]:
                    if aml.id == partial['credit_move_id']:
                        partials_values.append(partial)
                        ctp_aml_ids.append(partial['debit_move_id'])
                        partials_values_copy.remove(partial)

        # Filter available move line
        reconcile_domain = self.reconcile_domain and literal_eval(self.reconcile_domain) or []
        amls_to_filter = self.env['account.move.line'].browse(ctp_aml_ids)
        available_move_line_ids = amls_to_filter.filtered_domain(reconcile_domain).ids

        for partial in partials_values:
            if partial['debit_move_id'] in amls_to_matched.ids and partial['credit_move_id'] in available_move_line_ids:
                result.extend([{
                    'id': partial['debit_move_id'],
                    'amount': partial['amount_partial']
                }])
            elif partial['credit_move_id'] in amls_to_matched.ids and partial['debit_move_id'] in available_move_line_ids:
                result.extend([{
                    'id': partial['credit_move_id'],
                    'amount': partial['amount_partial']
                }])

        grouped_data = []
        for id_, items in groupby(result, key=lambda e: e['id']):
            total_amount = sum(item['amount'] for item in items)
            aml = self.env['account.move.line'].browse(id_)
            need_residual_line = aml.filtered(lambda x: x.account_id.reconcile or x.account_id.account_type in ('asset_cash', 'liability_credit_card'))
            amount_residual = need_residual_line and need_residual_line.balance - total_amount or 0.0
            # For the indicators related to accounts payable and advances, it is necessary to determine the outstanding amount or the advance amount.
            # For example:
            #     01/01/2024: Advance of $100
            #     01/02/2024: Invoice reconciliation of $20
            #     01/03/2025: Invoice reconciliation of $80.
            # As of 31/12/2025, when reviewing the 2024 report, the advance amount from customers is $80. In the 2025 report, the advance amount from customers is $0."
            grouped_data.append({'id': id_, 'amount': total_amount, 'amount_residual': amount_residual})
        return grouped_data
