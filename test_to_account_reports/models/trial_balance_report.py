import copy
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import groupby


# pylint: disable=consider-merging-classes-inherited
class TrialBalanceReport(models.Model):
    _inherit = 'account.report'

    def _get_customs_columns_header_trial_balance(self, columns_header):
        """
        As mentioned in _generate_columns, this method use to add Initial Balance before and End Balance after
        to columns header
        """
        self.ensure_one()
        column_count = len(self.column_ids)
        initial_balance_header = [{
            'name': _('Initial Balance'),
            'key': 'initial_balance',
            'colspan': column_count,
        }]
        end_balance_header = [{
            'name': _('End Balance'),
            'key': 'end_balance',
            'colspan': column_count,
        }]
        columns_header = initial_balance_header + columns_header + end_balance_header
        return columns_header

    def _get_customs_lines_trial_balance(self, filter_options, columns):
        """
        The Trail Balance report has following format:

        +-----------------+----------------+----------------+----------------+
        | Initial Balance |      2023      |      2022      |   End Balance  |
        +-----------------+----------------+----------------+----------------+
        | Debit | Credit  | Debit | Credit | Debit | Credit | Debit | Credit |
        +-----------------+----------------+----------------+----------------+

        In Which:
            - 2023, 2022: current period and comparison period. They might be 10/2023 and 11/2023,...
            - Initial Balance: normally initial balance is Debit if it's total balance of account is positive.
            Otherwise, it is Credit balance. For example: if total balance of bank account is 15.000 then Debit = 15.000 and Credit = 0.
            Otherwise, if its total balance is -15.000 then Debit = 0 and Credit = 15.000
            However, in some special cases. However, in some special cases such as accounts receivable/payable, they have balance at both
            debit and credit. These special accounts marked as 'show_both_dr_and_cr_trial_balance'.

            In this case:
            - If partner A has balance is 15.000 then debit = 15.000, credit = 0
            - If partner B has balance is -10.000 then debit = 0, credit = 10.000
            - If partner C has balane is -20.000 then debit = 0, credit = 20.000
            And now: total Debit = 15.000 and total Credit = 30.0000

        So the steps here are:
            1. Calculate Debit, Credit in current period
            2. Calculate Debit, Credit in comparison period if any
            3. Calculate Initial Balance:
                - 3.1: If comparison < current period then it's initial balance calculated to date_from of comparison period
                - 3.2: If comparison > current period or not comparison then it's initial balance calculated to date_from of current period
        """
        lines = []
        results = []
        comparison = filter_options['current_comparison'] and filter_options['current_comparison']['key'] != 'no_comparison'

        # query initial balance
        results += self._get_customs_lines_trial_balance_initial(filter_options, comparison=comparison)

        # query in period
        results += self._get_customs_lines_trial_balance_in_period(filter_options)

        # query comparison period
        if comparison:
            results += self._get_customs_lines_trial_balance_in_period(filter_options, comparison=True)

        # query ending balance
        results += self._get_customs_lines_trial_balance_ending(filter_options, comparison=comparison)
        results = sorted(results, key=lambda r: r['account_code'])

        new_results = self._merge_data(results, grouping_key=['account_id', 'account_code'])

        new_results = [el for el in new_results if any(
                el.get(key, 0.0) != 0.0
                for key in ['initial_balance_debit', 'initial_balance_credit', 'debit', 'credit', 'end_balance_debit', 'end_balance_credit']
            )
        ]

        account_ids = [r['account_id'] for r in new_results]
        for res in new_results:
            account = self.env['account.account'].browse(res['account_id']).with_prefetch(prefetch_ids=account_ids)
            if not account.include_initial_balance:
                end_balance = res.get('debit', 0.0) - res.get('credit', 0.0)
                res.update({
                    'initial_balance_debit': 0.0,
                    'initial_balance_credit': 0.0,
                    'end_balance_debit': end_balance if end_balance > 0 else 0,
                    'end_balance_credit': abs(end_balance) if end_balance < 0 else 0,
                })
            if account == account.company_id.get_unaffected_earnings_account():
                init_balance = res.get('initial_balance_debit', 0.0) - res.get('initial_balance_credit', 0.0)
                end_balance = init_balance + res.get('debit', 0.0) - res.get('credit', 0.0)
                res.update({
                    'initial_balance_debit': init_balance if init_balance > 0 else 0,
                    'initial_balance_credit': abs(init_balance) if init_balance < 0 else 0,
                    'end_balance_debit': end_balance if end_balance > 0 else 0,
                    'end_balance_credit': abs(end_balance) if end_balance < 0 else 0,
                })

            lines.append(self._prepare_customs_line_trial_balance_vals(filter_options, res, account, columns))

        line_total = self._prepare_trial_balance_line_total(new_results, columns)
        lines.append(line_total)

        return lines

    def _get_customs_lines_trial_balance_initial(self, filter_options, comparison=False):
        initial_options = self._get_initial_balance_option(filter_options)

        if comparison:
            comparison_options = self._get_comparison_option(filter_options)
            current_date_from = fields.Date.from_string(filter_options['current_date']['date_from'])
            comparison_date_from = fields.Date.from_string(comparison_options['current_date']['date_from'])
            date_to = min(current_date_from, comparison_date_from)
            date_to = date_to - timedelta(days=1)
            initial_options['current_date']['date_to'] = fields.Date.to_string(date_to)

        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': initial_options['current_date']['date_to']}
        })
        table, where_clauses, where_params = self._get_sql(initial_options, 'from_beginning')
        self.env['account.move.line'].flush_model()
        query = """
            WITH tmpl AS (SELECT
                account_move_line.account_id,
                account.code AS account_code,
                CASE WHEN SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) > 0 THEN
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision))
                    ELSE 0
                END AS debit_balance,
                CASE WHEN SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) < 0 THEN
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) * -1
                    ELSE 0
                END AS credit_balance
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN account_account account ON account.id = account_move_line.account_id
            WHERE {where_clauses}
            GROUP BY account_move_line.account_id, account.code, account_move_line.partner_id
            ORDER BY account.code)

            SELECT
                tmpl.account_id,
                tmpl.account_code,
                CASE WHEN account.show_both_dr_and_cr_trial_balance = True THEN
                    SUM(tmpl.debit_balance)
                    ELSE
                        CASE WHEN SUM(tmpl.debit_balance - tmpl.credit_balance) > 0 THEN
                            SUM(tmpl.debit_balance - tmpl.credit_balance)
                        ELSE 0 END
                    END AS initial_balance_debit,
                CASE WHEN account.show_both_dr_and_cr_trial_balance = True THEN
                    SUM(tmpl.credit_balance)
                    ELSE
                        CASE WHEN SUM(tmpl.debit_balance - tmpl.credit_balance) < 0 THEN
                            SUM(tmpl.credit_balance - tmpl.debit_balance)
                        ELSE 0 END
                    END AS initial_balance_credit
            FROM tmpl
            LEFT JOIN account_account account ON account.id = tmpl.account_id
            WHERE tmpl.debit_balance <> 0 OR tmpl.credit_balance <> 0
            GROUP BY tmpl.account_id, tmpl.account_code, account.show_both_dr_and_cr_trial_balance
            ORDER BY tmpl.account_code
        """.format(
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )
        self._cr.execute(query, where_params)
        data_trial_balance_initial = self._cr.dictfetchall()
        # For accounts that are not of the type include_initial_balance, such as revenue accounts, expense accounts, etc.,
        # expected that there will be no initial balance.
        data = self._recompute_trial_balance_initial(data_trial_balance_initial)
        return data

    def _get_customs_lines_trial_balance_in_period(self, filter_options, comparison=False):
        new_options = copy.deepcopy(filter_options)
        debit_column = 'debit'
        credit_column = 'credit'
        if comparison:
            new_options = self._get_comparison_option(filter_options)
            debit_column = 'comparison_debit'
            credit_column = 'comparison_credit'

        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': new_options['current_date']['date_to']}
        })
        table, where_clauses, where_params = self._get_sql(new_options, 'strict_range')
        self.env['account.move.line'].flush_model()
        query_in_period = """
            SELECT
                account_move_line.account_id,
                account.code AS account_code,
                SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)) AS {debit_column},
                SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)) AS {credit_column}
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN account_account account ON account.id = account_move_line.account_id
            WHERE {where_clauses}
            GROUP BY account_move_line.account_id, account.code
        """.format(
            debit_column=debit_column,
            credit_column=credit_column,
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )
        self._cr.execute(query_in_period, where_params)
        return self._cr.dictfetchall()

    def _get_customs_lines_trial_balance_ending(self, filter_options, comparison=False):
        new_options = copy.deepcopy(filter_options)
        if comparison:
            comparison_options = self._get_comparison_option(filter_options)
            current_date_to = fields.Date.from_string(filter_options['current_date']['date_to'])
            comparison_date_to = fields.Date.from_string(comparison_options['current_date']['date_to'])
            date_to = max(current_date_to, comparison_date_to)
            new_options['current_date']['date_to'] = fields.Date.to_string(date_to)

        currency_table = self.env['res.currency']._get_query_currency_table({
            'multi_company': True, 'date': {'date_to': new_options['current_date']['date_to']}
        })
        table, where_clauses, where_params = self._get_sql(new_options, 'from_beginning', extend_domain=[('account_id.include_initial_balance', '=', True)])
        self.env['account.move.line'].flush_model()
        query = """
            WITH tmpl AS (SELECT
                account_move_line.account_id,
                account.code AS account_code,
                CASE WHEN SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) > 0 THEN
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision))
                    ELSE 0
                END AS debit_balance,
                CASE WHEN SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) < 0 THEN
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) * -1
                    ELSE 0
                END AS credit_balance
            FROM {table}
            LEFT JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN account_account account ON account.id = account_move_line.account_id
            WHERE {where_clauses}
            GROUP BY account_move_line.account_id, account.code, account_move_line.partner_id
            ORDER BY account.code)

            SELECT
                tmpl.account_id,
                tmpl.account_code,
                CASE WHEN account.show_both_dr_and_cr_trial_balance = True THEN
                    SUM(tmpl.debit_balance)
                    ELSE
                        CASE WHEN SUM(tmpl.debit_balance - tmpl.credit_balance) > 0 THEN
                            SUM(tmpl.debit_balance - tmpl.credit_balance)
                        ELSE 0 END
                    END AS end_balance_debit,
                CASE WHEN account.show_both_dr_and_cr_trial_balance = True THEN
                    SUM(tmpl.credit_balance)
                    ELSE
                        CASE WHEN SUM(tmpl.debit_balance - tmpl.credit_balance) < 0 THEN
                            SUM(tmpl.credit_balance - tmpl.debit_balance)
                        ELSE 0 END
                    END AS end_balance_credit
            FROM tmpl
            LEFT JOIN account_account account ON account.id = tmpl.account_id
            WHERE tmpl.debit_balance <> 0 OR tmpl.credit_balance <> 0
            GROUP BY tmpl.account_id, tmpl.account_code, account.show_both_dr_and_cr_trial_balance
            ORDER BY tmpl.account_code
        """.format(
            table=table,
            currency_table=currency_table,
            where_clauses=where_clauses,
            )
        self._cr.execute(query, where_params)
        return self._cr.dictfetchall()

    def _prepare_customs_line_trial_balance_vals(self, filter_options, result, account, columns):
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
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': True,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_custom_line_columns(result, columns)
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

    def _prepare_trial_balance_line_total(self, results, columns):
        total_result = {
            'initial_balance_debit': sum(r.get('initial_balance_debit', 0) for r in results),
            'initial_balance_credit': sum(r.get('initial_balance_credit', 0) for r in results),
            'debit': sum(r.get('debit', 0) for r in results),
            'credit': sum(r.get('credit', 0) for r in results),
            'end_balance_debit': sum(r.get('end_balance_debit', 0) for r in results),
            'end_balance_credit': sum(r.get('end_balance_credit', 0) for r in results)
        }
        res = {
            'id': '~account.account~total',
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
            'columns': self._build_custom_line_columns(total_result, columns)
        }

        return res

    def _recompute_trial_balance_initial(self, data_trial_balance_initial):
        dict_account_ids = dict([(r['account_id'], r) for r in data_trial_balance_initial])
        account_ids = dict_account_ids.keys()
        accounts = self.env['account.account'].browse(account_ids).with_prefetch(prefetch_ids=account_ids)
        result = []
        for company, accounts in groupby(accounts, key=lambda acc: acc.company_id):
            balancing_account = company.get_unaffected_earnings_account()
            initial_balance = 0.0
            for account in accounts:
                if account.include_initial_balance:
                    result.append(dict_account_ids[account.id])
                else:
                    initial_balance += dict_account_ids[account.id]['initial_balance_debit'] - dict_account_ids[account.id]['initial_balance_credit']

            result.append({
                'account_id': balancing_account.id,
                'account_code': balancing_account.code,
                'initial_balance_debit': initial_balance if initial_balance > 0 else 0,
                'initial_balance_credit': abs(initial_balance) if initial_balance < 0 else 0
            })
        return result

    @api.model
    def _merge_data(self, data_vals, grouping_key=None):
        result = []
        if not grouping_key:
            return data_vals
        for key, lines in groupby(data_vals, key=lambda l: tuple(l[k] for k in grouping_key)):
            val = {
                k: v
                for k, v in zip(grouping_key, key)
            }
            for line in lines:
                for k in grouping_key:
                    line.pop(k)
                for k, v in line.items():
                    if k not in val:
                        val[k] = v
                    else:
                        val[k] += v
            result.append(val)
        return result
