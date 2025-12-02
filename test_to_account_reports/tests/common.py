from datetime import datetime
from unittest.mock import patch

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tools.misc import NON_BREAKING_SPACE


class AccountReportsCommon(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super(AccountReportsCommon, cls).setUpClass(chart_template_ref=chart_template_ref)

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        # Create accounting user.
        account_user = cls.env['res.users'].create({
            'name': 'Accountant',
            'login': 'accountant',
            'groups_id': [(6, 0, cls.env.user.groups_id.ids),
                          (4, cls.env.ref('account.group_account_user').id),
                          (4, cls.env.ref('account.group_account_manager').id),
                          (4, cls.env.ref('analytic.group_analytic_accounting').id)],
        })
        account_user.partner_id.email = 'accountantvn@example.viindoo.com'

        # Shadow the current environment/cursor with one having the report user.
        # This is mandatory to test access rights.
        cls.env = cls.env(user=account_user)
        cls.cr = cls.env.cr

        account_user.write({
            'company_ids': [(6, 0, (cls.company_data['company']).ids)],
            'company_id': cls.company_data['company'].id,
        })

        cls.customer_a = cls.env['res.partner'].create({
            'name': 'Customer A',
            'email': 'customera@viindoo.com',
        })

        cls.customer_b = cls.env['res.partner'].create({
            'name': 'Customer B',
            'email': 'customerb@viindoo.com',
        })

        cls.vendor_a = cls.env['res.partner'].create({
            'name': 'Vendor A',
            'email': 'vendora@viindoo.com',
        })

        cls.vendor_b = cls.env['res.partner'].create({
            'name': 'Vendor B',
            'email': 'vendorb@viindoo.com',
        })
        cls.vendor_c = cls.env['res.partner'].create({
            'name': 'Vendor C',
            'email': 'vendorc@viindoo.com',
        })
        # Default account for journal entry
        # 400000 Product Sales
        cls.default_account_revenue = cls.company_data['default_account_revenue']
        # 600000 Expenses
        cls.default_account_expense = cls.company_data['default_account_expense']
        # 110200 Stock Interim (Received)
        cls.default_account_stock = cls.company_data['default_account_stock']
        # 110300 Stock Interim (Delivered)
        cls.default_account_stock_delivered = cls.company_data['default_account_stock_delivered']
        # 500000 Cost of Goods Sold
        cls.default_account_type_direct_cost = cls.company_data['default_account_type_direct_cost']
        # 121000 Account Receivable
        cls.default_account_receivable = cls.company_data['default_account_receivable']
        # 211000 Account Payable
        cls.default_account_payable = cls.company_data['default_account_payable']
        # 201000 Current Liabilities
        cls.default_account_current_liabilities = cls.company_data['default_account_current_liabilities']
        # 291000 Non Current Liabilities
        cls.default_account_non_current_liabilities = cls.company_data['default_account_non_current_liabilities']
        # 101401 Bank
        cls.default_account_bank = cls.company_data['default_account_bank']
        # 101501 Cash
        cls.default_account_cash = cls.company_data['default_account_cash']
        # 301000 Capital
        cls.default_account_capital = cls.company_data['default_account_capital']
        # 441000 Foreign Exchange Gain
        cls.default_account_foreign = cls.company_data['default_account_foreign']
        # 191000 Non-Current Assets
        cls.default_account_non_assets = cls.company_data['default_account_non_assets']
        # 151000 Fixed Asset
        cls.default_account_fixed_assets = cls.company_data['default_account_fixed_assets']
        # 141000 Prepayments
        cls.default_account_prepayments = cls.company_data['default_account_prepayments']
        # 251000 Tax Received
        cls.default_account_tax_sale = cls.company_data['default_account_tax_sale']
        # 131000 Tax Paid
        cls.default_account_tax_purchase = cls.company_data['default_account_tax_purchase']

        # Default journal for journal entry
        cls.default_journal_misc = cls.company_data['default_journal_misc']
        cls.default_journal_sale = cls.company_data['default_journal_sale']
        cls.default_journal_purchase = cls.company_data['default_journal_purchase']
        cls.default_journal_bank = cls.company_data['default_journal_bank']
        cls.default_journal_cash = cls.company_data['default_journal_cash']

        cls.balancing_account = cls.company_data['company'].get_unaffected_earnings_account()

        # Default tax
        cls.tax_price_purchase_5 = cls.env['account.tax'].create({
            'name': '5% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_purchase_5 = cls.tax_price_purchase_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_purchase_10 = cls.env['account.tax'].create({
            'name': '10% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_purchase_10 = cls.tax_price_purchase_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_sale_5 = cls.env['account.tax'].create({
            'name': '5% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_sale_5 = cls.tax_price_sale_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_sale_10 = cls.env['account.tax'].create({
            'name': '10% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_sale_10 = cls.tax_price_sale_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        company_data = super().setup_company_data(company_name, chart_template=chart_template, **kwargs)

        company = company_data['company']
        chart_account = cls.env['account.account'].search([('company_id', '=', company.id)])

        accounts_vals = {
            'default_account_non_assets': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'asset_non_current')]),
            'default_account_fixed_assets': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'asset_fixed')]),
            'default_account_current_liabilities': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'liability_current')]),
            'default_account_non_current_liabilities': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'liability_non_current')]),
            'default_account_prepayments': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'asset_prepayments')]),
            'default_account_type_direct_cost': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'expense_direct_cost')]),
            'default_account_stock': cls._filtered_account(chart_account, chart_template, [('code', '=', '110200')]),
            'default_account_stock_delivered': cls._filtered_account(chart_account, chart_template, [('code', '=', '110300')]),
            'default_account_bank': cls._filtered_account(chart_account, chart_template, [('code', '=', '101404')]),
            'default_account_cash': cls._filtered_account(chart_account, chart_template, [('code', '=', '101501')]),
            'default_account_capital': cls._filtered_account(chart_account, chart_template, [('account_type', '=', 'equity')]),
            'default_account_foreign': cls._filtered_account(chart_account, chart_template, [('code', '=', '441000')]),
            'default_journal_misc': cls.env['account.journal'].search([
                    ('company_id', '=', company.id),
                    ('type', '=', 'general')
                ], limit=1),
        }
        # Create stock config.
        company_data.update(accounts_vals)
        return company_data

    def _init_journal_entry(self, partner, account_date, journal, **kwargs):
        """ Create a journal entry

        :param record partner: The partner in journal entry
        :param datetime account_date: The accounting date.
        :param record journal: The journal.
        :param dict kwargs: The journal items.
        Example:
            kwargs = {
                    'items': [{
                        'product_id': product id,
                        'account_id': account id (required),
                        'debit': debit amount,
                        'credit': credit amount,
                        'tag_ids': (6, 0, list tax id),
                        },
                        {
                        'product_id': product id,
                        'account_id': account id (required),
                        'debit': debit amount,
                        'credit': credit amount,
                        'tag_ids': (6, 0, list tax id),
                        }
                        ...............................
                        ]
                    }

        :return: A journal entry (account.move) record.
        """
        with self.patch_datetime_now(account_date), self.patch_date_today(account_date), self.patch_date_context_today(account_date):
            line_vals = []
            journal_items = kwargs.get('items', False)
            if journal_items:
                for value in journal_items:
                    line_vals.append((0, 0, value))
            val = {
                'partner_id': partner and partner.id or False,
                'date': account_date.date(),
                'journal_id': journal.id,
                'line_ids': line_vals
            }
            journal_entry = self.env['account.move'].with_context(tracking_disable=True).create(val)
            journal_entry.action_post()
        return journal_entry

    @classmethod
    def _filtered_account(cls, chart_account, chart_template, domain, **kwargs):
        field_name = kwargs.get('field_name', False)
        template_code = ''
        if field_name:
            template_code = chart_template[field_name].code
        account = None
        if template_code:
            account = chart_account.filtered_domain(domain + [('code', '=like', template_code + '%')])[:1]
        if not account:
            account = chart_account.filtered_domain(domain)[:1]
        return account

    def patch_datetime_now(self, now):
        return patch('odoo.fields.Datetime.now', return_value=now)

    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.today', return_value=today)

    def patch_date_context_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.context_today', return_value=today)

    def _get_lines_report(self, report, datetime, filter_option='today', date_from=None, date_to=None, cash_basis=False):
        """
        This method retrieves the report's rows.

        :param record report: The report object
        :param datetime datetime: Today
        :param char filter: the filter of the report ('today', 'custom', 'this_month', 'this_quarter', 'this_year', 'last_month', 'last_quarter', 'last_year')
        :param date date_from: The accounting period's start date
        :param date date_to: The accounting period's end date

        :return (list of dicts) The rows of the report
        """
        with self.patch_datetime_now(datetime), self.patch_date_today(datetime), self.patch_date_context_today(datetime):
            filter_options = self.env['account.report'].init_filter_options(report.id)
            for option_date_vals in filter_options['date_range']:
                if option_date_vals['key'] == filter_option:
                    if filter_option == 'custom':
                        option_date_vals.update({
                            'date_from': date_from and date_from.strftime('%Y-%m-%d') or '',
                            'date_to': date_to and date_to.strftime('%Y-%m-%d') or ''
                        })
                    filter_options['current_date'] = option_date_vals
                    break

            _columns_header, columns = report._generate_columns(filter_options)
            if cash_basis:
                filter_options['cash_basis'] = cash_basis
            lines = report._get_lines(filter_options, columns)
            return lines

    def _get_expanded_lines_report(self, report, line, datetime, filter_option='today', date_from=None, date_to=None, cash_basis=False):
        with self.patch_datetime_now(datetime), self.patch_date_today(datetime), self.patch_date_context_today(datetime):
            filter_options = self.env['account.report'].init_filter_options(report.id)
            for option_date_vals in filter_options['date_range']:
                if option_date_vals['key'] == filter_option:
                    if filter_option == 'custom':
                        option_date_vals.update({
                            'date_from': date_from and date_from.strftime('%Y-%m-%d') or '',
                            'date_to': date_to and date_to.strftime('%Y-%m-%d') or ''
                        })
                    filter_options['current_date'] = option_date_vals
                    break

            _columns_header, columns = report._generate_columns(filter_options)
            if cash_basis:
                filter_options['cash_basis'] = cash_basis
            return self.env['account.report.line'].get_expanded_lines(line=line, filter_options=filter_options, columns=columns)

    def _check_report_value(self, lines_to_check, line_expected_value):
        """
        This method for check the rows of the report

        :param list of dict lines: The rows value of the report
        :param list of tuple table_value: Expect value
        """
        # Check the report's line count
        self.assertEqual(len(lines_to_check), len(line_expected_value), "The number of lines reported is incorrect")
        # Check the value of each line in the report
        for index, line2check in enumerate(lines_to_check):
            line_expect = line_expected_value[index]

            self.assertEqual(line2check['id'], line_expect['id'])
            self.assertEqual(line2check['name'], line_expect['name'])

            for col_name, col_val in line_expect['columns'].items():
                block_value = line2check['columns'].get(col_name, {}).get('formatted_value') or ''
                output_value = self._prepare_output_value(block_value, col_val)

                self.assertEqual(output_value, block_value, "In the report line %s, the value is incorrect" % (index))

    def _prepare_output_value(self, block_value, output_value):
        if isinstance(output_value, str):
            return output_value
        if '$' in block_value:
            result = str('${}{:,.2f}'.format(NON_BREAKING_SPACE, output_value))
        elif '%' in block_value:
            result = str('{:,.1f}'.format(output_value)) + '%'
        elif not block_value and not output_value:
            result = ''
        else:
            result = str('{:,.1f}'.format(output_value))
        return result
