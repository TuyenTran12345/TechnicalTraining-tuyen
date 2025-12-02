from ast import literal_eval
import copy
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from datetime import timedelta
from odoo.osv import expression


class AccountReportLine(models.Model):
    _inherit = 'account.report.line'

    display_code = fields.Char(string='Display Code', help="Some countries require line code to be displayed on the reports. Ex. Vietnam."
                               " And because 'Code' field is unique identifier for all report, so sometime its value is not the value we"
                               " want to be displayed on the report. In this case, we use this field to display on the report.\n"
                               "Note: this field is only displayed on the report provided that the report is marked as Show Line Code")
    has_empty_row = fields.Boolean(string='Include Empty Row?', help="Some line has not any children and we want to separate them from other lines."
                                   " Then we need to mark the line has empty row. So it will have a blank line added below.")
    show_on_print_document = fields.Boolean(string='Show On Print Document', default=True,
                                 help="Technical field to indicate if this report line should display on pdf or xlsx printed.")
    duration_term = fields.Selection([
        ('none', 'N/A'),
        ('duration_3mo_orless', '3 Months or less'),
        ('duration_4mo_to_12mo', 'more than 3 month & less than 12 months'),
        ('duration_more_3mo', 'more than 3 months'),
        ('short_term', '12 months or less'),
        ('long_term', 'Non Current (more than 12 months)')], string='Duration Term', default='none', required=True)
    duration_term_date_field = fields.Char(string='Duration Term Date Field', default='date_maturity', required=True,
        help="The date field of journal item for usage with Duration Term. Default value is date_maturity (Due Date)")
    duration_term_direction = fields.Selection([
        ('past', 'To the Past'),
        ('future', 'To the Future')], string='Duration Term Direction',
        help="The direction of the Duration Term which is either:\n"
        "- To the Past: the condition will compare the data from the past.\n"
        "- To the Future: the condition will compare the data to the future\n")
    duration_term_account_type = fields.Selection([
        ('all', 'All'),
        ('not_asset_cash', 'Not Bank and Cash'),
        ('asset_cash', 'Bank and Cash')], string='Duration Term Base On', default='all',
        help="When calculating long-term and short-term lines, there are some lines need to calculate base on counter part account"
            " of Bank and Cash type or not or all")

    def _prepare_report_line_vals(self, filter_options, columns, exp_vals):
        """
        Hook method to prepare report line values.

        The report has 2 types of lines:
        1. account report line: these are the targets on the report
        2. expanded line: When clicking on a target that satisfies the condition, we need to display its details, including group by criteria.
        For example, the target 'Bank and Cash', when clicked, should display two accounts 'Bank Account', 'Cash Account' and the corresponding
        value of each account (group by account).

        Because there are 2 types of lines, we cannot use the id of self but need to generate the id in a specific format.
        line id can have complete information in the following format:

        ~account.report.line~3|groupby:account_id~account.account~2|groupby:partner_id~res.partner~1

        In which:
        - account.report.line is for line type 1 above
        - The numbers are the id of the corresponding record
        - |groupby: for expanded lines, shows that the line is a detail of a target and has been grouped by account_id

        So, the above example can be translated as follows: the current line is res.partner with id = 1 grouped by 'partner_id' and is a child of
        the previous line grouped by 'account_id' with account_id of 2. The previous line is a child of the account report line with id 3.

        This method is only for line type 1. Type 2 will be called from the client when the user clicks on a line to view details. That function
        is 'get_expanded_lines'. Therefore the id here is only in the form '~account.report.line~%s' % self.id

        For each line, in addition to the target name, we need to get the value of each line but it needs to correspond to each column.
        Because a report can be configured with multiple columns. Therefore we need to call the function '_build_line_columns'

        In addition, to serve the display on the client side, we need to add some other keys such as unfoldable, level, parent_id,...
        """
        self.ensure_one()
        line_class = 'account_report_level%s' % self.hierarchy_level
        if self.children_ids or not self.parent_id:
            line_class += ' fw-bolder'

        line_columns = self._build_line_columns(columns, exp_vals)

        unfoldable = any(line_columns[item]['unfoldable'] for item in line_columns) and filter_options.get('user_filter_unfold_all', False)

        visible = True
        if self.hide_if_zero and all(not line_columns[item]['value'] for item in line_columns):
            visible = False

        line = {
            'id': '~account.report.line~%s' % self.id,
            'name': self.name,
            'display_code': self.display_code or '',
            'level': self.hierarchy_level,
            'parent_id': self.parent_id.id or 0,
            'class': line_class,
            'columns': line_columns,
            'unfoldable': False if not self.groupby else unfoldable,
            'unfolded': False,
            'details_loaded': False,
            'groupby': self.groupby,
            'is_expanded_line': False,
            'visible': visible,
            'action_id': self.action_id.id or False,
            'has_empty_row': self.has_empty_row,
        }
        return line

    def _build_line_columns(self, columns, exp_vals):
        """
        As mentioned in the _prepare_report_line_vals function. For each line we need to determine the value of the line corresponding to each column

        Each column corresponds to an expression (identified by expression_name). Each expression itself has its value calculated and stored in the
        exp_vals parameter

        So we just need to rely on that to build columns corresponding to each line.
        """
        self.ensure_one()
        column_vals = {}

        for column in columns:
            value = ''
            unfoldable = False
            expression_id = False
            auditable = False
            formatted_value = ''
            column_class = ''
            green_on_positive = False
            for exp in exp_vals:
                if exp['line_code'] == self.code and exp['expression_key'] == column['key']:
                    value = exp.get('value', None)
                    formatted_value = exp.get('formatted_value', '')
                    unfoldable = exp.get('unfoldable', False)
                    expression_id = exp['expression_id']
                    auditable = exp['auditable']
                    green_on_positive = exp['green_on_positive']
                    column_class = self.env['account.report']._get_line_column_css_class(value)

            column_vals[column['key']] = {
                'value': value,
                'formatted_value': formatted_value,
                'unfoldable': unfoldable,
                'expression_id': expression_id,
                'auditable': auditable,
                'column_class': column_class,
                'green_on_positive': green_on_positive,
            }

        self.env['account.report']._update_comparison_percent_column(column_vals)

        return column_vals

    @api.model
    def get_expanded_lines(self, line, filter_options, columns):
        """
        When the user clicks on any target, we need to show the child lines of that target. These lines need to be grouped by one or more criteria
        Each target can be grouped by many criteria. For example: 'Bank and Cash' target maybe grouped by 'account_id' and 'partner_id'.
        Now, if the user clicks on 'Bank and Cash target', it will show account move line grouped by account_id. Continue clicking on any account,
        for example 'Bank Account', it will show account move line grouped by partner id whose account_id is 'Bank Account'

        If has comparison then line['columns'] contain comparison column with key has startswith is 'comparison'. In this case, we need only
        re-calculate date_from, date_to of filter_options

        @param line: current line user clicked on. It used to get expanded lines. In case this line is customs line, meaning it has not
        data of account.report.line and account.report.expression, for example: General Ledger, Trial Balance,... then this method will redirect to
        '_get_customs_expanded_lines' method of account.report model

        """
        if line.get('is_customs_line', False):
            return self.env['account.report']._get_customs_expanded_lines(line, filter_options, columns)

        lines = []
        if not line.get('groupby', False):
            return lines

        # group by has form: account_id,partner_id
        # TODO: validate group by fields
        groupby = line['groupby'].replace(' ', '')
        groupby = groupby.split(',')
        next_groupby = ','.join(groupby[1:]) if len(groupby) > 1 else None
        groupby = groupby[0]
        groupby_model = self.env['account.move.line']._fields[groupby].comodel_name

        expression_ids = [val['expression_id'] for val in line['columns'].values()]
        # as we know, the report maybe has many columns and Each column has an expression to calculate its value
        # therefore we need to loop through the columns to determine the value of each corresponding expanded line
        results = []
        exp_report = self.env['account.report.expression']
        expression_id = 0
        for key, value in line['columns'].items():
            # we do not calculate with percent column because it calculated in other method when build columns
            if key != 'percent':
                # handle comparison
                new_options = copy.deepcopy(filter_options)
                if key.startswith('comparison'):
                    new_options['current_date']['date_from'] = filter_options['current_comparison']['date_from']
                    new_options['current_date']['date_to'] = filter_options['current_comparison']['date_to']

                expression_id = value['expression_id']
                exp_report = self.env['account.report.expression'].browse(expression_id).with_prefetch(prefetch_ids=expression_ids)
                extend_domain = []
                # in case the user clicks on expand line to further expand its child lines. For example: click on 'Bank Account'
                # to show corresponding partners. Then we need add extend domain to filter by account_id is 'Bank Account'
                # to get account_id, we need parse line id has form:
                # ~account.report.line~3|groupby:account_id~account.account~2|groupby:partner_id~res.partner~1
                if line['is_expanded_line']:
                    split_line_ids = line['id'].split('|groupby:')[-1].split('~')
                    if split_line_ids:
                        extend_domain = [(split_line_ids[0], '=', int(split_line_ids[2]))]

                domain = literal_eval(exp_report.formula) if exp_report.formula and exp_report.engine == 'domain' else []
                domain = expression.AND([domain, extend_domain])
                # handle domain for duration term (Short/Long-term)
                if exp_report.engine in ('tax_tags', 'domain', 'account_codes'):
                    duration_term_domain = exp_report.report_line_id._prepare_duration_term_domain(filter_options['current_date']['date_to'])
                    domain = expression.AND([domain, duration_term_domain])

                table, where_clauses, where_params = self.env['account.report']._get_sql(new_options, exp_report.date_scope, extend_domain=domain)

                partial_reconcile_vals = []
                if exp_report.use_reconcile:
                    query = f"""
                        SELECT account_move_line.id
                        FROM {table}
                        WHERE {where_clauses}
                    """
                    self._cr.execute(query, where_params)
                    query_result = self._cr.dictfetchall()
                    move_line_ids = [res['id'] for res in query_result]
                    move_lines = self.env['account.move.line'].browse(move_line_ids).with_prefetch(prefetch_ids=move_line_ids)
                    move_lines_debit = move_lines.filtered('debit')
                    move_lines_credit = move_lines.filtered('credit')
                    partial_reconcile_vals = exp_report._get_partial_reconcile_value(move_lines_debit, filter_options, date_scope=exp_report.date_scope)
                    partial_reconcile_vals.extend(exp_report._get_partial_reconcile_value(move_lines_credit, filter_options, date_scope=exp_report.date_scope))

                currency_table = self.env['res.currency']._get_query_currency_table({
                    'multi_company': True, 'date': {'date_to': new_options['current_date']['date_to']}
                    })
                query = """
                    SELECT
                        {groupby},
                        COALESCE(SUM(account_move_line.balance * currency_table.rate), 0.0) AS {key}
                    FROM {table}
                    JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
                    WHERE {where_clauses}
                    GROUP BY {groupby}
                """.format(
                    groupby=groupby,
                    key=key,
                    table=table,
                    currency_table=currency_table,
                    where_clauses=where_clauses,
                    )

                self._cr.execute(query, where_params)
                query_results = self._cr.dictfetchall()

                # Handle partial reconcile
                if partial_reconcile_vals:
                    # Clear value of key in query_results
                    for res in query_results:
                        res[key] = 0.0

                    for res in query_results:
                        for partial_reconcile_val in partial_reconcile_vals:
                            aml = self.env['account.move.line'].browse(partial_reconcile_val['id'])
                            if res[groupby] == aml[groupby].id:
                                if exp_report.use_amount_residual:
                                    res[key] += partial_reconcile_val['amount_residual']
                                else:
                                    res[key] += partial_reconcile_val['amount']

                for res in query_results:
                    if res[key]:
                        if exp_report.subformula:
                            if 'sum_if_pos' in exp_report.subformula:
                                if res[key] > 0:
                                    results.append(res)
                            elif 'sum_if_neg' in exp_report.subformula:
                                if res[key] < 0:
                                    results.append(res)
                            else:
                                if res[key] != 0:
                                    results.append(res)
                        else:
                            if res[key] != 0:
                                results.append(res)

        # result of 'results' maybe include lines of previous comparison. For example: we have 2 lines:
        # - line1: Purchase costs account, 200K of this period
        # - line2: Purchase costs account, 100K of previous period
        # in this case, we have merged these lines with 2 column: one for this period, one for previous period
        # conditions for merge these lines is groupby, groupby maybe 'account_id', 'partner_id',...
        # so, we need handle and replace 'results' to 'new_results'.
        new_results = []
        for res in results:
            exists_groupby_id = [new_res[groupby] for new_res in new_results]
            # if not exists groupby then add to new results
            if res[groupby] not in exists_groupby_id:
                new_results.append(res)
            # else then add column by using update new result
            else:
                for new_res in new_results:
                    if new_res[groupby] == res[groupby]:
                        for key, value in res.items():
                            if key != groupby:
                                new_res.update({key: value})

        groupby_res_ids = [r[groupby] for r in new_results]
        for res in new_results:
            groupby_record = self.env[groupby_model].browse(res[groupby]).with_prefetch(prefetch_ids=groupby_res_ids)
            new_line = {
                'id':  "%s|groupby:%s~%s~%s" % (line['id'], groupby, groupby_model, res[groupby]),
                'name': groupby_record.display_name or _("Unknown"),
                'display_code': '',
                'level': line['level'] + 1,
                'parent_id': line['id'] or 0,
                'class': 'account_report_level%s' % (line['level'] + 1),
                'columns': self.env['account.report']._build_custom_line_columns(res, columns, report_expression=exp_report),
                'unfoldable': True if next_groupby else False,
                'unfolded': False,
                'is_expanded_line': True,
                'visible': True,
                'groupby': next_groupby,
                'details_loaded': False,
            }
            lines.append(new_line)
        return lines

    def _prepare_duration_term_domain(self, date_to):
        domain = []
        date_to = fields.Date.from_string(date_to)
        if self.duration_term == 'none':
            return domain

        if self.duration_term_direction == 'past':
            date_due = date_to - relativedelta(months=12) + timedelta(days=1)
            date_midle = date_to - relativedelta(months=3) + timedelta(days=1)
            if self.duration_term == 'short_term':  # <= 12 months
                if self.duration_term_account_type == 'not_asset_cash':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'),
                                        '|',
                                            (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            (self.duration_term_date_field, '=', False),
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'),
                                        '|', '|', '|', '|',
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '=', False),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '=', False),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                elif self.duration_term_account_type == 'asset_cash':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'),
                                        '|',
                                            (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            (self.duration_term_date_field, '=', False),
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'),
                                        '|', '|', '|', '|',
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '=', False),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '=', False),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                        (self.duration_term_date_field, '=', False)]
                else:
                    domain += ['|', (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')), (self.duration_term_date_field, '=', False)]
            elif self.duration_term == 'long_term':  # > 12 months
                if self.duration_term_account_type == 'not_asset_cash':
                    domain += ['|',
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'), (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d'))]
                elif self.duration_term_account_type == 'asset_cash':
                    domain += ['|',
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'), (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d'))]
                else:
                    domain += [(self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_3mo_orless':  # <= 3 months
                domain += [(self.duration_term_date_field, '>=', date_midle.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_4mo_to_12mo':  # > 3 months and <= 12 months
                domain += [(self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                           (self.duration_term_date_field, '<', date_midle.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_more_3mo':  # > 3 months
                domain += [(self.duration_term_date_field, '<', date_midle.strftime('%Y-%m-%d'))]
        else:
            date_due = date_to + relativedelta(months=12)
            date_midle = date_to + relativedelta(months=3)

            if self.duration_term == 'short_term':  # <= 12 months
                if self.duration_term_account_type == 'not_asset_cash':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'),
                                        '|',
                                        (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                        (self.duration_term_date_field, '=', False),
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'),
                                        '|', '|', '|', '|',
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '=', False),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '=', False),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                elif self.duration_term_account_type == 'asset_cash':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'),
                                        '|',
                                        (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                        (self.duration_term_date_field, '=', False),
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'),
                                        '|', '|', '|', '|',
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '=', False),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '=', False),
                                            '&', '&',
                                            ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                else:
                    domain += ['|', (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')), (self.duration_term_date_field, '=', False)]
            elif self.duration_term == 'long_term':  # > 12 months
                if self.duration_term_account_type == 'not_asset_cash':
                    domain += ['|',
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'), (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d'))]
                elif self.duration_term_account_type == 'asset_cash':
                    domain += ['|',
                                    '&', ('ctp_account_ids.account_type', '=', 'asset_cash'), (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.account_type', '!=', 'asset_cash'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d'))]
                else:
                    domain += [(self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_3mo_orless':  # <= 3 months
                domain += ['|', (self.duration_term_date_field, '<=', date_midle.strftime('%Y-%m-%d')), (self.duration_term_date_field, '=', False)]
            elif self.duration_term == 'duration_4mo_to_12mo':  # > 3 months and <= 12 months
                domain += [(self.duration_term_date_field, '>', date_midle.strftime('%Y-%m-%d')),
                           (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_more_3mo':  # > 3 months
                domain += [(self.duration_term_date_field, '>', date_midle.strftime('%Y-%m-%d'))]
        return domain
