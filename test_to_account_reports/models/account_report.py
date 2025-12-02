import calendar
import copy
import io
import json

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from babel.dates import get_quarter_names
from ast import literal_eval
# pylint: disable=missing-manifest-dependency
from bs4 import BeautifulSoup
from markupsafe import Markup

from odoo import fields, models, api, _
from odoo.tools.misc import format_date
from odoo.tools.misc import formatLang
from odoo.tools.misc import xlsxwriter
from odoo.osv import expression
from odoo.addons.web.controllers.utils import clean_action


SUPPORTED_PRINTING_FORMATS = ['pdf', 'xlsx']


class AccountReport(models.Model):
    _inherit = 'account.report'

    show_line_code = fields.Boolean(string='Show Line Code', help="Some countries require line code to be displayed on the reports. Ex. Vietnam."
                                    " If this field checked then 'Display Code' of all lines will be displayed on this report.")
    custom_line_python_function_suffix = fields.Char(string='Python Function Suffix for Customs Lines', help="This is technical field"
                                    " used when a report does not use existing rules, also known as report lines."
                                    " For example: General Ledger, Partner Ledger,... these reports will define"
                                    " python functions to generate the customs lines they want."
                                    " this functions must has suffix to identify. This field set by developer when create new report")
    custom_line_name_template = fields.Char(string='Template for Custom Line Name')
    # for printing
    custom_report_header_template = fields.Char(string='Custom Report Header Template',
                                                help="""Custom header template for printing report templates.
                                                        Useful when you want to customize different print layouts for each country or each type of report you want.""")
    custom_report_body_template = fields.Char(string='Custom Report Body Template',
                                              help="""Custom body template for printing report templates.
                                                      Useful when you want to customize different print layouts for each country or each type of report you want.""")
    custom_report_footer_template = fields.Char(string='Custom Report Footer Template',
                                                help="""Custom footer template for printing report templates.
                                                        Useful when you want to customize different print layouts for each country or each type of report you want.""")
    template_ref = fields.Char(string='Reference', translate=True)

    @api.model
    def init_report_data(self, context_report_id, custom_line_name_template, **kwgs):
        """
        When load report, we need to load same initial data: report variants, journal and current report.
        These data will not be reloaded unless changing the report variant or refresh browser
        """
        available_reports, current_report = self._get_available_reports(context_report_id, custom_line_name_template, **kwgs)

        return {
            'reports': available_reports,
            'current_report': current_report,
        }

    @api.model
    def init_filter_options(self, report_id, option_params=None):
        """
        There are all the options used to show or hide options on filter panel with corresponding data.

        The values of this option will only be changed on the client side unless we call the function generate_report_data.
        Then we need to recalculate the date from, date to, date string. The other values of the option will not be changed.
        """
        if not report_id:
            return {}

        account_report = self.browse(report_id)
        # initialize date range and current date
        date_range = account_report._get_date_range()
        current_date = next((d for d in date_range if d['key'] == account_report.default_opening_date_filter), date_range[0])

        filter_options = {
            'report_id': account_report.id,
            'use_filter_date_range': account_report.filter_date_range,
            'user_filter_unfold_all': account_report.filter_unfold_all,
            'use_filter_period_comparison': account_report.filter_period_comparison,
            'use_filter_growth_comparison': account_report.filter_growth_comparison,
            'use_filter_account_type': account_report.filter_account_type,
            'use_filter_analytic': account_report.filter_analytic,
            'use_filter_journals': account_report.filter_journals,
            'use_filter_partner': account_report.filter_partner,
            'use_filter_show_draft': account_report.filter_show_draft,
            'use_filter_unreconciled': account_report.filter_unreconciled,
            'date_filter': account_report.default_opening_date_filter,
            'date_range': date_range
        }

        if not option_params:
            filter_options['include_unposted_entry'] = False
            filter_options['unfold_all'] = False
            filter_options['account_type'] = self._get_account_type()
            filter_options['display_account_type'] = self._get_display_account_type()
            filter_options['current_date'] = current_date
            filter_options['partner_ids'] = []
            filter_options['journal_ids'] = []
            filter_options['analytic_account_ids'] = []
            # initialize comparisons and current comparison
            comparisons, current_comparison = self._get_comparison(filter_options)
            filter_options['comparisons'] = comparisons
            filter_options['current_comparison'] = current_comparison
        else:
            filter_options['include_unposted_entry'] = option_params.get('include_unposted_entry', False)
            filter_options['unfold_all'] = option_params.get('unfold_all', False)
            filter_options['account_type'] = option_params.get('account_type', self._get_account_type())
            filter_options['display_account_type'] = option_params.get('display_account_type', self._get_display_account_type())
            filter_options['current_date'] = option_params.get('current_date', current_date)
            filter_options['partner_ids'] = option_params.get('partner_ids', [])
            filter_options['journal_ids'] = option_params.get('journal_ids', [])
            filter_options['analytic_account_ids'] = option_params.get('analytic_account_ids', [])
            comparisons, current_comparison = self._get_comparison(filter_options)
            filter_options['comparisons'] = option_params.get('comparisons', comparisons)
            filter_options['current_comparison'] = option_params.get('current_comparison', current_comparison)

        return filter_options

    def _get_available_reports(self, context_report_id, custom_line_name_template, **kwgs):
        """
        Context report passed from client action. This report maybe have some variants.
        So this function will calculate and return the report with its variants

        If this report has many variants, we need to define default report (current report) among its variants.
        Current report calculated based on availability condition of the report:
            - If availability condition is 'coa': current report = report of coa of env company
            - If availability condition is 'country': current report = report of country of env company
        """
        context_report = self.browse(context_report_id)
        available_reports = []
        current_report = context_report._update_current_report_vals({'custom_line_name_template': custom_line_name_template})
        reports = context_report + context_report.variant_report_ids
        reports = reports.filtered(lambda r: not r.root_report_id or r.availability_condition == 'always'
                                    or (r.availability_condition == 'country' and not r.country_id)
                                    or (r.availability_condition == 'coa' and not r.chart_template_id)
                                    or (r.availability_condition == 'coa' and r.chart_template_id and r.chart_template_id == self.env.company.chart_template_id)
                                    or (r.availability_condition == 'country' and r.country_id and r.country_id == self.env.company.account_fiscal_country_id))
        for report in reports:
            if not report.custom_line_name_template:
                custom_line_name_template = 'to_account_reports.AccountReportLineNameDefault'
            elif '.' in report.custom_line_name_template:
                custom_line_name_template = report.custom_line_name_template
            else:
                custom_line_name_template = 'to_account_reports.%s' % report.custom_line_name_template

            available_reports.append({
                'id': report.id,
                'name': report.display_name,
                'custom_line_name_template': custom_line_name_template
            })

        # handle current report
        for report in reports:
            if report.availability_condition == 'coa' and report.chart_template_id and report.chart_template_id == self.env.company.chart_template_id:
                report._update_current_report_vals(current_report)
                break

            if report.availability_condition == 'country' and report.country_id and report.country_id == self.env.company.account_fiscal_country_id:
                report._update_current_report_vals(current_report)

        return available_reports, current_report

    def _update_current_report_vals(self, current_report):
        self.ensure_one()

        if current_report.get('custom_line_name_template'):
            custom_line_name_template = current_report['custom_line_name_template']
        elif not self.custom_line_name_template:
            custom_line_name_template = 'to_account_reports.AccountReportLineNameDefault'
        elif '.' in self.custom_line_name_template:
            custom_line_name_template = self.custom_line_name_template
        else:
            custom_line_name_template = 'to_account_reports.%s' % self.custom_line_name_template

        current_report['id'] = self.id
        current_report['name'] = self.display_name
        current_report['custom_line_name_template'] = custom_line_name_template
        return current_report

    def _get_journals(self):
        """
        Get all journals by env company
        """
        res = [{
            'id': 0,
            'name': _("All Journals")
        }]
        journals = self.env['account.journal'].with_context(active_test=False).search([
            ('company_id', '=', self.env.company.id)
        ])
        for journal in journals:
            res.append({
                'id': journal.id,
                'name': journal.name,
            })
        return res

    def _get_account_type(self):
        """
        Account type options used to map with displayed account type:
            - Display account type used to show account type options on filter on client side
            - Account type options used to determine which type to select.
            That is, when the user selects an option, its corresponding value will be True.

        We declare it here for easy extension.
        """
        return {
            'receivable': True,
            'non_trade_receivable': False,
            'payable': True,
            'non_trade_payable': False,
        }

    def _get_display_account_type(self):
        """
        Display account type used to show account type options on client side.
        We declare it here for easy extension.
        """
        return {
            'receivable': _("Receivable"),
            'non_trade_receivable': _("Non Trade Receivable"),
            'payable': _("Payable"),
            'non_trade_payable': _("Non Trade Payable"),
        }

    def _get_date_range(self):
        """
        We need filter report by a few date range or custom date: today, this month, this year,...
        So, this method used to prepare the date range to display on client side and calculate date from, date to, date string.
        Date string used to display date range after user selected
        Date from and date to calculated base on fiscal year of env company and filter date range option of the report.
        So this method cannot be api.model
        """
        self.ensure_one()
        if self.filter_date_range:
            date_range = [
                {'key': 'today', 'string': _('Today')},
                {'key': 'this_month', 'string': _('This Month')},
                {'key': 'this_quarter', 'string': _('This Quarter')},
                {'key': 'this_year', 'string': _('This Financial Year')},
                {'key': 'last_month', 'string': _('Last Month')},
                {'key': 'last_quarter', 'string': _('Last Quarter')},
                {'key': 'last_year', 'string': _('Last Financial Year')},
            ]
        else:
            date_range = [
                {'key': 'today', 'string': _('Today')},
                {'key': 'last_month', 'string': _('End of Last Month')},
                {'key': 'last_quarter', 'string': _('End of Last Quarter')},
                {'key': 'last_year', 'string': _('End of Last Financial Year')},
            ]

        date_range.append({'key': 'custom', 'string': _('Custom'), 'date_from': False, 'date_to': False, 'date_string': _('Custom')})

        for date in date_range:
            date_option = date['key']
            today = fields.Date.context_today(self)
            dt_from = False
            dt_to = False

            # handle date from, date to, date string
            if date_option == 'today':
                company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Datetime.now())
                dt_from = company_fiscalyear_dates['date_from']
                dt_to = today
            elif date_option == 'this_month':
                dt_from = today.replace(day=1)
                dt_to = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            elif date_option == 'this_quarter':
                quarter = (today.month - 1) // 3 + 1
                dt_to = (today.replace(month=quarter * 3, day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
                dt_from = dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year)
            elif date_option == 'this_year':
                company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Datetime.now())
                dt_from = company_fiscalyear_dates['date_from']
                dt_to = company_fiscalyear_dates['date_to']
            elif date_option == 'last_month':
                dt_to = today.replace(day=1) - timedelta(days=1)
                dt_from = dt_to.replace(day=1)
            elif date_option == 'last_quarter':
                quarter = (today.month - 1) // 3 + 1
                quarter = quarter - 1 if quarter > 1 else 4
                dt_to = (today.replace(month=quarter * 3, day=1, year=today.year if quarter != 4 else today.year - 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
                dt_from = dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year)
            elif date_option == 'last_year':
                max_day_in_month_last_year = calendar.monthrange(today.year - 1, today.month)[1]
                day = today.day if today.day <= max_day_in_month_last_year else max_day_in_month_last_year
                company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Datetime.now().replace(year=today.year - 1, day=day))
                dt_from = company_fiscalyear_dates['date_from']
                dt_to = company_fiscalyear_dates['date_to']

            if dt_from:
                date['date_from'] = fields.Date.to_string(dt_from)
            if dt_to:
                date['date_to'] = fields.Date.to_string(dt_to)
            if dt_from and dt_to:
                date['date_string'] = self._format_date_string(dt_from, dt_to, date_option, self.filter_date_range)

        return date_range

    @api.model
    def _format_date_string(self, dt_from, dt_to, date_option, filter_date_range):
        """
        This method used to format date to string to display on client side:
            - 01/01/2023 - 01/07/2023 => From 01/01/2023 to 01/07/20223
            - This Month => May 2023
        """
        if not filter_date_range:
            return _('As of %s') % (format_date(self.env, fields.Date.to_string(dt_to)),)
        if 'month' in date_option:
            return format_date(self.env, fields.Date.to_string(dt_to), date_format='MMMM yyyy').title()
        if 'quarter' in date_option:
            quarter = (dt_to.month - 1) // 3 + 1
            return (u'%s\N{NO-BREAK SPACE}%s') % (get_quarter_names('abbreviated', locale=self._context.get('lang') or 'en_US')[quarter], dt_to.year)
        if 'year' in date_option:
            if self.env.company.fiscalyear_last_day == 31 and int(self.env.company.fiscalyear_last_month) == 12:
                return dt_to.strftime('%Y')
            else:
                return '%s - %s' % ((dt_to.year - 1), dt_to.year)
        if 'today' in date_option and not filter_date_range:
            return _('As of %s') % (format_date(self.env, fields.Date.to_string(dt_to)),)

        return _('From %s <br/> to  %s').replace('<br/>', '\n') % (format_date(self.env, fields.Date.to_string(dt_from)), format_date(self.env, fields.Date.to_string(dt_to)))

    @api.model
    def _get_comparison(self, filter_options):
        """
        Similar to _get_date_range, this method use to show filter that allow user to compare between periods.
        """
        comparisons = filter_options.get('comparisons', [])
        current_date = filter_options['current_date']
        filter_period_comparison = filter_options['use_filter_period_comparison']
        filter_date_range = filter_options['use_filter_date_range']
        current_comparison = filter_options.get('current_comparison', {})

        if not filter_period_comparison:
            return comparisons, current_comparison

        if not comparisons:
            comparisons = [
                {'key': 'no_comparison', 'string': _('No Comparison'), 'date_string': _('No Comparison')},
                {'key': 'previous_period', 'string': _('Previous Period'), 'date_string': 'Previous Period'},
                {'key': 'same_period_last_year', 'string': _('Same Period Last Year'), 'date_string': 'Same Period Last Year'},
                {'key': 'custom', 'string': _('Custom'), 'date_string': _('Custom Comparison'), 'date_from': False, 'date_to': False}
            ]

        for comparison in comparisons:
            comparison_key = comparison['key']
            if comparison_key == 'custom' and comparison.get('date_from', False) and comparison.get('date_to', False):
                dt_from = fields.Date.from_string(comparison['date_from'])
                dt_to = fields.Date.from_string(comparison['date_to'])
            else:
                dt_from = current_date['date_from']
                dt_to = current_date['date_to']
                if isinstance(dt_to, (str,)):
                    dt_to = fields.Date.from_string(dt_to)
                if dt_from and isinstance(dt_from, (str,)):
                    dt_from = fields.Date.from_string(dt_from)
                date_option = current_date['key']

                if comparison_key == 'no_comparison' or comparison_key == 'custom':
                    continue

                if comparison_key == 'same_period_last_year' or date_option in ('this_year', 'last_year'):
                    dt_to = dt_to + relativedelta(years=-1)
                    if dt_from:
                        dt_from = dt_from + relativedelta(years=-1)
                    else:
                        company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(dt_to)
                        dt_from = company_fiscalyear_dates['date_from']
                else:
                    if date_option == 'today':
                        dt_to = dt_from + relativedelta(days=-1)
                        dt_from = dt_from + relativedelta(years=-1)
                    elif date_option in ('this_month', 'last_month'):
                        dt_from = (dt_from - timedelta(days=1)).replace(day=1)
                        dt_to = dt_to.replace(day=1) - timedelta(days=1)
                    elif date_option in ('this_quarter', 'last_quarter'):
                        dt_to = dt_to.replace(month=(dt_to.month + 10) % 12, day=1) - timedelta(days=1)
                        dt_from = dt_from and dt_from.replace(month=dt_to.month - 2, year=dt_to.year) or dt_from
                    elif date_option == 'custom':
                        if dt_from:
                            dt_from = dt_from + relativedelta(days=-1)
                            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(dt_from)
                            dt_to = dt_from
                        else:
                            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(dt_to + relativedelta(days=-1))
                            dt_to = dt_to + relativedelta(months=-1)
                            dt_to = dt_to + relativedelta(day=31)

                        dt_from = company_fiscalyear_dates['date_from']

            comparison['date_from'] = fields.Date.to_string(dt_from)
            comparison['date_to'] = fields.Date.to_string(dt_to)
            comparison['date_string'] = self._format_date_string(dt_from, dt_to, date_option, filter_date_range)

        if not current_comparison:
            current_comparison = comparisons[0]
        else:
            current_comparison = next((c for c in comparisons if c['key'] == current_comparison['key']), comparisons[0])

        return comparisons, current_comparison

    @api.model
    def generate_report_data(self, report_id, filter_options):
        """
        This method called after user select options on the filter panel. It generate report data: columns_header, columns, line and lines

        Besides, after generate data, we need re-calculate some options in filter and return it to use in client side
        """
        res = {
            'columns_header': [],
            'columns': [],
            'lines': [],
        }

        report = self.browse(report_id)
        if not report.exists():
            return res

        partner_names = []
        analytic_account_names = []
        if filter_options['partner_ids']:
            partner_names = self._get_partner_names(filter_options['partner_ids'])  # see _get_partner_names method
        if filter_options['analytic_account_ids']:
            analytic_account_names = self._get_analytic_names(filter_options['analytic_account_ids'])  # see _get_analytic_names method

        current_date = filter_options['current_date']
        if current_date['key'] == 'custom':
            dt_from = fields.Date.from_string(current_date['date_from'])
            dt_to = fields.Date.from_string(current_date['date_to'])
            current_date['date_string'] = self._format_date_string(dt_from, dt_to, 'custom', filter_options['use_filter_date_range'])
            filter_options['current_date'] = current_date

        current_comparison = filter_options['current_comparison']
        if current_comparison:
            if current_comparison['key'] == 'custom':
                dt_from = fields.Date.from_string(current_comparison['date_from'])
                dt_to = fields.Date.from_string(current_comparison['date_to'])
                current_comparison['date_string'] = self._format_date_string(dt_from, dt_to, 'custom', filter_options['use_filter_date_range'])
                filter_options['current_comparison'] = current_comparison
            else:
                comparisons, current_comparison = self._get_comparison(filter_options)
                filter_options['comparisons'] = comparisons
                filter_options['current_comparison'] = current_comparison

        columns_header, columns = report._generate_columns(filter_options)

        res['columns_header'] = columns_header
        res['columns'] = columns
        res['show_line_code'] = report.show_line_code
        res['lines'] = report._get_lines(filter_options, columns)
        res['partner_names'] = partner_names
        res['analytic_account_names'] = analytic_account_names
        res['filter_options'] = filter_options

        return res

    def _get_partner_names(self, partner_ids):
        """
        After use select partner to filter. We need show their name on report content.

        In there, partner_ids passed from client side
        """
        partners = self.env['res.partner'].search_read(['|', '&',
            ('company_id', '=', False),
            ('company_id', '=', self.env.company.id),
            ('id', 'in', partner_ids),
        ], fields=['name'])

        return ', '.join([p['name'] for p in partners])

    def _get_analytic_names(self, account_ids):
        """
        Similar to _get_partner_names
        """
        partners = self.env['account.analytic.account'].search_read(['|', '&',
            ('company_id', '=', False),
            ('company_id', '=', self.env.company.id),
            ('id', 'in', account_ids),
        ], fields=['name'])

        return ', '.join([p['name'] for p in partners])

    def _generate_columns(self, filter_options):
        """
        On the report, we have 2 types of dynamic columns:
            - Header Columns: they are columns representing date range, periods comparison, percentage comparison,...
            - Columns: they are columns of a report line that are declared when defining the report. Ex. Debit, Credit,...

        Each header column contains columns of the report line: Today (Debit, Credit). Previous Period (Debit, Credit),...
        with Today, Previous Period are columns header and Debit, Credit are columns

        In case of comparison, we need to add additional columns corresponding to the period to be compared.
        If there is only 1 column to compare, we need to add a percentage column

        In some case, if the report want to add custom columns before or after then it must be define custom method with format
        '_get_customs_columns_header_%s' % self.custom_line_python_function_suffix
        """
        self.ensure_one()
        column_count = len(self.column_ids)
        columns_header = [{
            'name': filter_options['current_date']['date_string'],
            'colspan': column_count,
        }]
        columns = []

        if filter_options['current_comparison'] and filter_options['current_comparison']['key'] != 'no_comparison':
            columns_header.append({
                'key': 'comparison',
                'name': filter_options['current_comparison']['date_string'],
                'colspan': column_count,
            })
            if column_count == 1:
                columns_header.append({
                    'key': 'percent',
                    'name': '%',
                    'colspan': column_count,
                })

        if self.custom_line_python_function_suffix:
            function_name = '_get_customs_columns_header_%s' % self.custom_line_python_function_suffix
            if hasattr(self, function_name):
                columns_header = getattr(self, function_name)(columns_header)

        report_columns = self.column_ids.sorted(key=lambda c: c.sequence)

        for header in columns_header:
            columns += report_columns._prepare_column_vals_list(header)

        return columns_header, columns

    def _get_lines(self, filter_options, columns):
        """
        We need to show the lines and values corresponding to each column of each line on the report.
        For example, we need to have a report showing 3 columns Debit, Credit and Balance. Then, the results we need to display
        are Lines 1, Debit = 5, Credit = 3 and Balance = 2

        For the configuration to be reported as above, on each line we need to create 3 expressions:
        - Expression 1: Name = debit, expression = ... (expression to calculate value = 5)
        - Expression 2: Name = credit, expression = ... (expression to calculate value = 3)
        - Expression 3: Name = balance, expression = ... (expression to calculate value = 2)

        Then on the report.column_ids report (not on the line), we create 3 columns:
        - Column 1: Name = Debit, Expression Label = debit (identical to the Name of expression 1 above)
        - Column 2: Name = Credit, Expression Label = credit (identical to Name of expression 2 above)
        - Column 3: Name = Balance, Expression Label = balance (identical to the Name of expression 3 above)

        Finally, the report will show lines and 3 columns Debit, Credit and Balance. In there:
        - Line 1: the Debit column will rely on the Expression Label as debit to find the value of the expression with
        Name = debit and fill in this column.
        - Same with the next lines

        In summary:
        - Each line can have many expressions, each expression has its key Name. The report can have many columns, each column will be mapped
        with the Name of the expression through the column.expression_label field to get the value corresponding to each line.
        - Lines are uniquely identified through a code field and their value will be used throughout the reporting system through this
        unique code field.


        So the algorithm here is:
        - Step 1: From the list of all lines, get the list of all expressions and then call the expressions._cal_expression_values function to
        calculate the values of all expressions. The return result of this step will be in the form:
        [
            {'line_code': 'BA', 'expression_name': 'debit', 'value': 5},
            {'line_code': 'BA', 'expression_name': 'credit', 'value': 2},
            {'line_code': 'BA', 'expression_name': 'balance', 'value': 3},
            {'line_code': 'REC', 'expression_name': 'debit', 'value': 7},
            {'line_code': 'REC', 'expression_name': 'credit', 'value': 6},
            {'line_code': 'REC', 'expression_name': 'balance', 'value': 1},
            ...
        ]

        - Step 2: map the passed columns with the above list to get the value corresponding to each column and each line. The result returned
        after mapping has the following form:
        [
            {'line_code': 'BA', 'debit': 5, 'credit': 2, 'balance': 3},
            {'line_code': 'REC', 'debit': 7, 'credit': 6, 'balance': 1},
            ...
        ]
        In addition, you can add some additional information for display purposes outside the report such as: line_id, level, parent_id,...

        - Step 3: In case there is a comparison, repeat the above two steps but with the dates filter of the comparison. The returned result
        if there is a comparison will be as follows:
        [
            {'line_code': 'BA', 'debit': 5, 'credit': 2, 'balance': 3, 'pre_debit': 9, 'pre_credit': 5, 'pre_balance': 4},
            {'line_code': 'REC', 'debit': 7, 'credit': 6, 'balance': 1, 'pre_debit': 15, 'pre_credit': 8, 'pre_balance': 7},
            ...
        ]

        """
        self.ensure_one()
        exp_vals = self.line_ids.expression_ids._cal_expression_values(filter_options)
        if filter_options['current_comparison'] and filter_options['current_comparison']['key'] != 'no_comparison':
            new_options = self._get_comparison_option(filter_options)
            exp_vals += self.line_ids.expression_ids._cal_expression_values(new_options, comparison=True)

        lines = []
        report_lines = self.line_ids.sorted(lambda r: r.sequence)
        for line in report_lines:
            lines.append(line._prepare_report_line_vals(filter_options, columns, exp_vals))

        # see _get_customs_lines method
        customs_lines = self._get_customs_lines(filter_options, columns)
        for customs_line in customs_lines:
            lines.append(customs_line)

        return lines

    def _get_customs_lines(self, filter_options, columns):
        """
        Some report have not any lines defined in account report line like Balance Sheet, P&L,...
        They has only columns and their lines will be generated according to each need
        They called customs lines and generated by custom methods according to each need with format name is
        '_get_customs_lines_%s' % self.custom_line_python_function_suffix

        To generate custom lines for each report then that report must have 'custom_line_python_function_suffix'
        """
        self.ensure_one()
        if not self.custom_line_python_function_suffix:
            return []
        function_name = '_get_customs_lines_%s' % self.custom_line_python_function_suffix
        if not hasattr(self, function_name):
            return []
        return getattr(self, function_name)(filter_options, columns)

    @api.model
    def _get_customs_expanded_lines(self, line, filter_options, columns):
        """
        As mentioned in get_expanded_lines methods. This method generate expanded line of custom line
        See get_expanded_lines method for more details

        Because custom lines generated by custom method according to each need, customs_expanded_lines
        is also generate by custom expanded line method with format
        '_get_customs_expanded_lines_%s' % account_report.custom_line_python_function_suffix like _get_customs_lines
        """
        lines = []
        report_id = filter_options.get('report_id', False)
        if not report_id:
            return lines

        account_report = self.browse(report_id)
        if not account_report.custom_line_python_function_suffix:
            return lines

        function_name = '_get_customs_expanded_lines_%s' % account_report.custom_line_python_function_suffix
        return getattr(self, function_name)(line, filter_options, columns)

    @api.model
    def action_open_auditable(self, line, column_key, filter_options):
        """
        This method called when user click on a value of a column. It redirect to account move line action
        with the domain corresponding to that value
        """
        if not line.get('columns') or not line['columns'].get(column_key) or not line['columns'][column_key].get('expression_id'):
            return False

        column = line['columns'][column_key]
        new_options = copy.deepcopy(filter_options)
        if column_key.startswith('comparison'):
            new_options = self._get_comparison_option(filter_options)

        action = {
            'name': _("Journal Items"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'list',
            'views': [(False, 'list')],
        }

        report_exp = self.env['account.report.expression'].browse(column['expression_id'])
        if report_exp.auditable:
            domain = []
            if report_exp.engine == 'domain' and report_exp.formula:
                domain = literal_eval(report_exp.formula)
            elif report_exp.engine == 'tax_tags' and report_exp.formula:
                tags = report_exp._get_matching_tags()
                domain = [('tax_tag_ids', 'in', tags.ids)]

            # handle domain for duration term (Short/Long-term)
            if report_exp.engine in ('tax_tags', 'domain', 'account_codes'):
                duration_term_domain = report_exp.report_line_id._prepare_duration_term_domain(filter_options['current_date']['date_to'])
                domain = expression.AND([domain, duration_term_domain])

            domain = expression.AND([domain, self._build_domain_from_options(new_options, report_exp.date_scope)])

            if line['is_expanded_line']:
                split_line_ids = line['id'].split('|groupby:')
                split_line_ids.pop(0)
                expand_domain = []
                for item in split_line_ids:
                    split_item = item.split('~')
                    if split_item:
                        if split_item[2] == 'None':
                            expand_domain += [(split_item[0], '=', False)]
                        else:
                            expand_domain += [(split_item[0], '=', int(split_item[2]))]

                if expand_domain:
                    domain = expression.AND([domain, expand_domain])

            action['domain'] = domain

        return action

    @api.model
    def open_line_action(self, line, filter_options):
        """
        This method called when user click on a line to redirect some where, ex. from Executive Summary to Balance Sheet,...
        """
        if line.get('action_dict', {}):
            return line['action_dict']

        if not line.get('action_id'):
            return False

        tmpl_action = self.env['ir.actions.actions'].sudo().browse(line['action_id'])
        action = self.env[tmpl_action.type].sudo().browse(line['action_id'])
        res = clean_action(action.read()[0], env=action.env)

        if tmpl_action.type == 'ir.actions.client' and action.tag == 'account_report':
            # if destination action is other account report. We need pass filterOption of source to destination report
            # to ensure filter of destination must be the same source report
            res.update({'params': {'filterOptions': filter_options}})

        return res

    @api.model
    def _get_sql(self, filter_options, date_scope, extend_domain=None):
        """
        Prepare domain based on formula of line and filter_options then return get_sql()

        :param dict filter_options: options passed from client.
        :param str date_scope: Normally this is the date_scope will be get from filter_options (date_from, date_to).
        However, in some cases, date scope can be overridden by expression or cross report. For example: the 'Current Year Earnings'
        item of the Balance Sheet is taken from the 'Net Profit' target of the P&L. At that time, we need to use the expression of 'Net Profit'
        to calculate the value but we want to use the date_scope of 'Current Year Earnings' because the indicator we need to show is
        'Current Year Earnings', not 'Net Profit'. In this case, date_scope will be passed
        :param extend_domain: when we need to generate expanded lines of item, we need to add some special domains of these lines.
        In this case, extend_domain will be passed
        """
        domain = self._build_domain_from_options(filter_options, date_scope) + [('display_type', 'not in', ('line_section', 'line_note'))]
        if extend_domain:
            domain = expression.AND([domain, extend_domain])
        query = self.env['account.move.line']._search(domain)
        table, where_clauses, where_params = query.get_sql()
        return table, where_clauses, where_params

    @api.model
    def _build_domain_from_options(self, filter_options, date_scope):
        """
        This method return domain based on filter options. It can use for sql query,...
        """
        domain = []

        # Filter by State
        if not filter_options.get('include_unposted_entry', False):
            domain += [('parent_state', '=', 'posted')]
        else:
            domain += [('parent_state', '!=', 'cancel')]

        # Filter by Dates
        # normally we will use date from and date to in options. However, some expressions have a special date_scope like 'from_fiscalyear'
        # then we need to recalculate date_from according to this date scope
        current_date = filter_options.get('current_date', False)
        if current_date:
            mode = 'in_range' if filter_options.get('use_filter_date_range', False) else 'at_time'
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
                        domain += [('date', '>=', date_from)]

                domain += [('date', '<=', date_to)]

        # Filter by Partners
        partner_ids = filter_options.get('partner_ids', [])
        if partner_ids:
            domain += [('partner_id', 'in', partner_ids)]

        # Filter by Journals
        journal_ids = filter_options.get('journal_ids', [])
        if journal_ids:
            domain += [('journal_id', 'in', journal_ids)]

        # Filter by Account Type
        account_type = filter_options.get('account_type', {})
        if filter_options.get('use_filter_account_type', False) and account_type:
            account_type_domain = []
            if account_type['receivable']:
                account_type_domain.append([('account_id.account_type', '=', 'asset_receivable'), ('account_id.non_trade', '=', False)])
            if account_type['non_trade_receivable']:
                account_type_domain.append([('account_id.account_type', '=', 'asset_receivable'), ('account_id.non_trade', '=', True)])
            if account_type['payable']:
                account_type_domain.append([('account_id.account_type', '=', 'liability_payable'), ('account_id.non_trade', '=', False)])
            if account_type['non_trade_payable']:
                account_type_domain.append([('account_id.account_type', '=', 'liability_payable'), ('account_id.non_trade', '=', True)])

            if account_type_domain:
                account_type_domain = expression.OR(account_type_domain)
                domain = expression.AND([domain, account_type_domain])

        if filter_options.get('analytic_account_ids', []):
            domain += [('analytic_distribution', 'in', filter_options['analytic_account_ids'])]

        return domain

    @api.model
    def _format_value(self, value, figure_type, blank_if_zero, force_currency=None):
        """
        Value need to format based on figure_type and blank_if_zero before show in report.
        """
        if figure_type == 'none' or value == '':
            return value

        if figure_type == 'monetary':
            currency = force_currency or self.env.company.currency_id
            if blank_if_zero and currency.is_zero(value):
                return ''
            if currency.is_zero(value):
                value = abs(value)
            return formatLang(self.env, value, currency_obj=currency)

        if figure_type == 'float':
            return formatLang(self.env, value or 0.0, digits=1)

        if figure_type == 'integer':
            return formatLang(self.env, value or 0.0, digits=0)

        if figure_type in ('date', 'datetime'):
            return format_date(self.env, value)

        if figure_type == 'percentage':
            formatted_value = formatLang(self.env, value, digits=1)
            return f"{formatted_value}%"

        return value

    @api.model
    def _build_custom_line_columns(self, line, columns, report_expression=None):
        """
        Each row needs to have columns with corresponding values. This method build columns of a custom line base one
        data of the line and columns of report
        """
        columns_dict = {}

        for column in columns:
            value = 0
            formatted_value = ''
            expression_id = 0
            auditable = False
            column_class = ''
            figure_type = None
            blank_if_zero = False
            green_on_positive = report_expression.green_on_positive if report_expression else False
            if column['key'] != 'percent':
                if column['figure_type'] in ('monetary', 'percentage', 'integer', 'float'):
                    value = line.get(column['key'], 0)
                else:
                    value = line.get(column['key'], '')
                if report_expression:
                    expression_id = report_expression.id
                    value = report_expression._handle_subformula(value)
                    if report_expression.auditable and value is not None:
                        auditable = True

                figure_type = column['figure_type']
                blank_if_zero = column['blank_if_zero']
                formatted_value = self._format_value(value, figure_type, blank_if_zero)
                column_class = self._get_line_column_css_class(value)

                if column['key'] == 'amount_currency':
                    formatted_value = ''
                    currency_id = line.get('currency_id', False)
                    if currency_id:
                        currency = self.env['res.currency'].browse(line['currency_id'])
                        if currency != self.env.company.currency_id:
                            formatted_value = self._format_value(value, figure_type, blank_if_zero, force_currency=currency)

            columns_dict.update({
                column['key']: {
                    'value': value,
                    'formatted_value': formatted_value,
                    'unfoldable': False,
                    'expression_id': expression_id,
                    'auditable': auditable,
                    'column_class': column_class,
                    'figure_type': figure_type,
                    'blank_if_zero': blank_if_zero,
                    'green_on_positive': green_on_positive,
                }
            })

        self._update_comparison_percent_column(columns_dict)

        return columns_dict

    @api.model
    def _get_line_column_css_class(self, value):
        column_class = []
        if isinstance(value, (int, float)):
            column_class.append('text-end')
            if value < 0:
                column_class.append('text-danger')
        return ' '.join(column_class)

    @api.model
    def _update_comparison_percent_column(self, columns_dict):
        """
        We need calculate comparison percentage after build line columns and update to columns_dict
        percent = ((value1 - value2) / abs(value2)) * 100 and it's value formatted is success or danger
        based on green_on_positive of column
        """
        column_key_list = list(columns_dict.keys())
        if len(column_key_list) == 3 and 'percent' in column_key_list:
            value1 = columns_dict[column_key_list[0]].get('value', 0)
            value2 = columns_dict[column_key_list[1]].get('value', 0)
            value = 0
            formatted_value = 'n/a'
            column_class = 'text-end'
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                value = value1 - value2
                value = ((value1 - value2) / abs(value2)) * 100 if value2 else 0
                if not value2 and value1:
                    formatted_value = 'n/a'
                else:
                    formatted_value = self._format_value(value, 'percentage', False, force_currency=None)

                green_on_positive = columns_dict[column_key_list[0]].get('green_on_positive', False)
                if green_on_positive:
                    if value > 0:
                        column_class += ' text-success'
                    elif value < 0:
                        column_class += ' text-danger'
                else:
                    if value > 0:
                        column_class += ' text-danger'
                    elif value < 0:
                        column_class += ' text-success'

            columns_dict[column_key_list[2]]['value'] = value
            columns_dict[column_key_list[2]]['formatted_value'] = formatted_value
            columns_dict[column_key_list[2]]['column_class'] = column_class

        return columns_dict

    @api.model
    def _get_initial_balance_option(self, filter_options):
        """
        This method create new initial balance options from filter options and it may re-use for Trial Balance and General Ledger
        """
        new_options = copy.deepcopy(filter_options)
        current_date = new_options.get('current_date', False)
        if current_date:
            date_to = fields.Date.from_string(current_date['date_from']) - timedelta(days=1)

            new_options['current_date']['date_from'] = None
            new_options['current_date']['date_to'] = fields.Date.to_string(date_to)

        return new_options

    @api.model
    def _get_comparison_option(self, filter_options):
        new_options = copy.deepcopy(filter_options)
        new_options['current_date']['date_from'] = filter_options['current_comparison']['date_from']
        new_options['current_date']['date_to'] = filter_options['current_comparison']['date_to']
        return new_options

    def action_export_report(self, data, output_format):
        if output_format not in SUPPORTED_PRINTING_FORMATS:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        return {
            'type': 'ir_actions_af_report_dl',
            'data': {
                'report_data': json.dumps(data),
                'output_format': output_format,
                'report_id': self.id,
                'company_id': self.env.company.id,
            }
        }

    def get_circular_code(self):
        return ''

    def get_export_templates(self):
        return {
            'header_template': self.custom_report_header_template,
            'body_template': self.custom_report_body_template or 'to_account_reports.account_report_print_body_default',
            'footer_template': self.custom_report_footer_template or 'web.internal_layout',
        }

    def get_export_filename(self):
        """ The name that will be used for the file when downloading pdf,xlsx,..."""
        self.ensure_one()
        return self.name.lower().replace(' ', '_')

    def _prepare_pdf_context(self, report_data):
        base_url = (self.env['ir.config_parameter'].sudo().get_param('report.url')
                    or self.env['ir.config_parameter'].sudo().get_param('web.base.url'))
        return {
            'mode': 'print',
            'report': self,
            'base_url': base_url,
            'company': self.env.company,
            'company_currency': self.env.company.currency_id.name,
            'body_html': self._clean_content_html_for_pdf(report_data.get('body_html', '')),
            'options': report_data['filter_options'],
            'report_data': report_data,
            # Accountant does not have access right to chart template so add sudo is needed
            'chart_template': self.chart_template_id.sudo() or self.env.company.chart_template_id.sudo(),
        }

    def _prepare_wkhtmltopdf_options(self, rcontext):
        return {
            'landscape': rcontext['report_data']['report_width'] > 1000,
            'specific_paperformat_args': {
                'data-report-margin-top': 10,
                'data-report-margin-bottom': 30,
                'data-report-header-spacing': 15,
            }
        }

    @api.model
    def _clean_content_html_for_pdf(self, content_html):
        soup = BeautifulSoup(content_html, 'html.parser')
        # convert a href="#" to div to prevent hash link clickable in the pdf
        for link in soup.select('a[href="#"]'):
            link.name = 'div'
        return str(soup)

    def _render_pdf(self, report_data):
        templates = self.get_export_templates()
        rcontext = self._prepare_pdf_context(report_data)
        body_context = {
            **rcontext,
            'body_template': templates['body_template'],
        }
        body = self.env['ir.ui.view']._render_template(
            'to_account_reports.account_report_print_template',
            values=body_context
        )
        header = bytes('', 'utf-8')
        if templates['header_template']:
            header_body = self.env['ir.actions.report']._render_template(templates['header_template'], values=rcontext)
            header = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=Markup(header_body.decode())))
        footer = bytes('', 'utf-8')
        if templates['footer_template']:
            footer_body = self.env['ir.actions.report']._render_template(templates['footer_template'], values=rcontext)
            footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=Markup(footer_body.decode())))
        wkhtmltopdf_opts = self._prepare_wkhtmltopdf_options(rcontext)
        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body.unescape()],
            header=header.decode(),
            footer=footer.decode(),
            landscape=wkhtmltopdf_opts['landscape'],
            specific_paperformat_args=wkhtmltopdf_opts['specific_paperformat_args']
        )

    @api.model
    def _get_report_columns_for_excel(self, report_data):
        if report_data['lines'] and '~account.report.line~' in report_data['lines'][0]['id']:
            init_columns_header = [{'name': _('Items'), 'rowspan': 2, 'colspan': 3}]
        else:
            init_columns_header = [{'name': '', 'rowspan': 2, 'colspan': 3}]
        init_columns = [{'name': '', 'colspan': 3}]
        if report_data['show_line_code']:
            init_columns_header.extend([{'name': _('Code'), 'rowspan': 2}])
            init_columns.extend([{'name': ''}])
        for col_header in report_data['columns_header']:
            if col_header.get('key', '') == 'percent':
                col_header['rowspan'] = 2
        return {
            'columns_header': init_columns_header + report_data['columns_header'],
            'columns': init_columns + report_data['columns'],
        }

    def _prepare_xlsx_values(self, workbook, sheet, report_data):
        company = self.env.company
        address_items = [company.street, company.street2, company.city, company.state_id.name, company.country_id.name]
        address = ', '.join([item for item in address_items if item])
        columns = self._get_report_columns_for_excel(report_data)
        return {
            'report_data': report_data,
            'company': company,
            'company_address': address,
            'columns': columns,
            'num_table_col': sum([col.get('colspan', 1) for col in columns['columns_header']]),
            'formats': {
                'report_code_style': workbook.add_format(
                    {'font_name': 'Arial', 'align': 'center', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
                'report_code_bold_style': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'align': 'center', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1}),
                'def_style': workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'title_style': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'align': 'center', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1,
                     'num_format': '#,##0'}),
                'title_style_vcenter': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1,
                     'num_format': '#,##0'}),
                'level_0_style': workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_0_style_bold': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_1_style': workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_1_style_bold': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_2_style': workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_2_style_bold': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_3_style': workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'level_3_style_bold': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'style_bold': workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0'}),
                'style_indent': workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0', 'indent': 2}),
                'style_indent_bold':  workbook.add_format(
                    {'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': '#,##0', 'indent': 2,
                     'bold': True}),
                'content_style_left': workbook.add_format({
                    'align': 'left',
                    'font_name': 'Arial',
                    'font_size': 13
                }),
                'title_report_format': workbook.add_format({
                    'bold': True,
                    'font_name': 'Arial',
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 16
                }),
                'currency_format': workbook.add_format({
                    'align': 'left',
                    'font_size': 12,
                    'text_wrap': True,
                    'font_name': 'Arial'
                }),
                'date_format': workbook.add_format({
                    'align': 'center',
                    'font_size': 12,
                    'text_wrap': True,
                    'font_name': 'Arial'
                }),
                'template_ref_title_format': workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'font_name': 'Arial',
                    'font_size': 13
                }),
                'template_ref_circular_format': workbook.add_format({
                    'align': 'center',
                    'font_name': 'Arial',
                    'font_size': 13
                }),
                'footer_content_center': workbook.add_format({
                    'align': 'center',
                    'font_name': 'Arial',
                    'font_size': 12
                }),
                'footer_content_center_bold': workbook.add_format({
                    'align': 'center',
                    'font_name': 'Arial',
                    'font_size': 11,
                    'bold': True
                }),
            },
            'start_row': 9,
            'x_offset': 0,
        }

    def _write_xlsx_header(self, sheet, values, x_offset, y_offset):
        # write header
        content_style_left = values['formats']['content_style_left']
        sheet.write(0, 0, '   ' + _('Company: ') + values['company'].name, content_style_left)
        sheet.write(1, 0, '   ' + _('Address: ') + values['company_address'], content_style_left)

    def _write_xlsx_body(self, sheet, values, x_offset, y_offset):
        report_data = values['report_data']
        options = report_data['filter_options']
        lines = list(filter(lambda l: l['visible'], report_data['lines']))
        start_row = values['start_row']
        columns = values['columns']
        num_table_col = values['num_table_col']
        column_header_width_default = 12
        for key, value in columns.items():
            for v in value:
                width = len(v.get('name', ''))
                if width > column_header_width_default:
                    column_header_width_default = width
        title_style = values['formats']['title_style']
        title_style_vcenter = values['formats']['title_style_vcenter']
        # write table column header + sub header
        for col_name, col_vals in columns.items():
            x = x_offset
            for col in col_vals:
                column_name = col.get('name', '').replace('\n', ' ')
                colspan = col.get('colspan', 1)
                rowspan = col.get('rowspan', 1)
                if colspan > 1 or rowspan > 1:
                    col_header_style = title_style
                    if rowspan > 1:
                        title_style_vcenter.set_align('center')
                        title_style_vcenter.set_align('vcenter')
                        col_header_style = title_style_vcenter
                    sheet.merge_range(y_offset, x, y_offset + (rowspan - 1), x + (colspan - 1), column_name,
                                      col_header_style)
                    x += colspan
                else:
                    sheet.write(y_offset, x, column_name, title_style)
                    x += 1
            y_offset += 1
        line_name_width_default = 90
        line_name_width = max([len(str(line['name'])) for line in report_data['lines']] + [line_name_width_default])
        line_column_max_width_map = defaultdict(int)
        for d in (line['columns'] for line in report_data['lines']):
            for key, value in d.items():
                content = str(value['value'])
                line_column_max_width_map[key] = max(line_column_max_width_map[key], len(content))
        line_column_max_width_map = {
            i: line_column_max_width_map[col] + 5
            for i, col in enumerate(line_column_max_width_map, start=1)
        }
        visited_line_columns = set()
        set_width_line_name = False
        # merge 3 cols for line name
        line_name_colspan = 3
        for y, line in enumerate(lines):
            line_bold = False
            style_str = f"level_{line['level']}_style"
            if 'fw-bold' in line['class'] or line.get('unfolded'):
                line_bold = True
                style_str += "_bold"
            style = values['formats'].get(style_str, values['formats']['def_style'])
            x = x_offset
            # write line name
            _line_name_style = style
            if line['parent_id']:
                if 'fw-bold' in line['class'] or line.get('unfolded'):
                    _line_name_style = values['formats']['style_bold']
                    if line['level'] > 2:
                        _line_name_style = values['formats']['style_indent_bold']
                else:
                    if line['level'] > 2:
                        _line_name_style = values['formats']['style_indent']
            if not set_width_line_name:
                if line_name_colspan > 1:
                    sheet.set_column(x, x + line_name_colspan - 1, line_name_width / line_name_colspan)
                else:
                    sheet.set_column(x, x, line_name_width)
                set_width_line_name = True
            # merge 3 cols for line name
            if line_name_colspan > 1:
                sheet.merge_range(y + y_offset, x, y + y_offset, x + (line_name_colspan - 1), line['name'],
                                  _line_name_style)
                x += line_name_colspan
            else:
                sheet.write(y + y_offset, x, line['name'], _line_name_style)
                x += 1
            # write code
            if report_data['show_line_code']:
                _line_code_style = values['formats']['report_code_style']
                if line_bold:
                    _line_code_style = values['formats']['report_code_bold_style']
                sheet.write(y + y_offset, x, line['display_code'], _line_code_style)
                x += 1
            # write line columns
            col_index = 0
            cols = x
            line_columns = [val for val in line['columns'].values()]
            for x in range(cols, len(line['columns']) + cols):
                _line_column_style = style
                if line_bold:
                    _line_column_style = values['formats']['style_bold']
                col_index += 1
                line_col = line_columns[col_index - 1]
                sheet.write(y + y_offset, x, line_col['value'], _line_column_style)
                if col_index not in visited_line_columns:
                    sheet.set_column(x, x, max(line_column_max_width_map[col_index], column_header_width_default))
                    visited_line_columns.add(col_index)

        # Add title, currency, date into file excel
        sheet.merge_range(start_row - 4, x_offset, start_row - 4, num_table_col + x_offset - 1, self.name.upper(),
                          values['formats']['title_report_format'])
        sheet.merge_range(start_row - 3, x_offset, start_row - 3, num_table_col + x_offset - 1,
                          options['current_date']['date_string'], values['formats']['date_format'])
        sheet.write(start_row - 1, x_offset - 1 + num_table_col, _('Currency: %s') % self.env.company.currency_id.name,
                    values['formats']['currency_format'])

    def _write_xlsx_footer(self, sheet, values, x_offset, y_offset):
        total_row = sheet.dim_rowmax + 1
        num_table_col = values['num_table_col']
        footer_content_center = values['formats']['footer_content_center']
        footer_content_center_bold = values['formats']['footer_content_center_bold']
        if num_table_col >= 5:
            total_row = sheet.dim_rowmax + 1
            sheet.write(total_row + 3, x_offset, _('Prepared By'), footer_content_center_bold)
            sheet.write(total_row + 4, x_offset, _('(Signature, Full Name)'), footer_content_center)

            sheet.merge_range(total_row + 3, x_offset + num_table_col // 3, total_row + 3,
                              x_offset + num_table_col // 3 + 1, _('Chief Accountant'), footer_content_center_bold)
            sheet.merge_range(total_row + 4, x_offset + num_table_col // 3, total_row + 4,
                              x_offset + num_table_col // 3 + 1, _('(Signature, Full Name)'), footer_content_center)

            sheet.merge_range(total_row + 2, x_offset + num_table_col - 2, total_row + 2,
                              x_offset + num_table_col, _('Month ..... Day ..... Year .....'),
                              footer_content_center)
            sheet.merge_range(total_row + 3, x_offset + num_table_col - 2, total_row + 3,
                              x_offset + num_table_col, _('Director/CEO'), footer_content_center_bold)
            sheet.merge_range(total_row + 4, x_offset + num_table_col - 2, total_row + 4,
                              x_offset + num_table_col, _('(Signature, Full Name, Job Title)'),
                              footer_content_center)
        else:
            sheet.write('A{}'.format(total_row + 3), _('Prepared By'), footer_content_center_bold)
            sheet.write('A{}'.format(total_row + 4), _('(Signature, Full Name)'), footer_content_center)

            sheet.write('B{}'.format(total_row + 3), _('Chief Accountant'), footer_content_center_bold)
            sheet.write('B{}'.format(total_row + 4), _('(Signature, Full Name)'), footer_content_center)

            sheet.merge_range('C{0}:D{0}'.format(total_row + 2), _('Month ..... Day ..... Year .....'),
                              footer_content_center)
            sheet.merge_range('C{0}:D{0}'.format(total_row + 3), _('Director/CEO'), footer_content_center_bold)
            sheet.merge_range('C{0}:D{0}'.format(total_row + 4), _('(Signature, Full Name, Job Title)'),
                              footer_content_center)

    def _render_xlsx(self, workbook, report_data):
        sheet = workbook.add_worksheet(self.name[:31])
        sheet.set_default_row(20)
        sheet.fit_to_pages(1, 1)
        if len(report_data['columns']) > 5:
            sheet.set_landscape()
        values = self._prepare_xlsx_values(workbook, sheet, report_data)
        start_row = values['start_row']  # row start of the table
        x_offset = values['x_offset']
        y_offset = start_row
        num_table_col = values['num_table_col']
        if num_table_col >= 5:
            x_offset = 0

        # Header
        self._write_xlsx_header(sheet, values, x_offset, y_offset)
        # Body
        self._write_xlsx_body(sheet, values, x_offset, y_offset)
        # Footer
        self._write_xlsx_footer(sheet, values, x_offset, y_offset)
        # A4
        sheet.set_paper(9)
        sheet.print_area(0, 0, sheet.dim_rowmax, sheet.dim_colmax)

    def render_xlsx(self, report_data):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        self._render_xlsx(workbook, report_data)
        workbook.close()
        output.seek(0)
        file_content = output.read()
        output.close()
        return file_content
