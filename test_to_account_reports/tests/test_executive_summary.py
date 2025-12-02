from datetime import datetime
from odoo.tests.common import tagged
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class ExecutiveSummary(AccountReportsCommon):

    def setUp(self):
        super(ExecutiveSummary, self).setUp()
        self.AccountExecutiveSummary = self.env.ref('to_account_reports.executive_summary_report')

    def test_01_validate_executive_summary(self):
        # 01/01/2021 Capital contribution 70000 cash
        journal_items_1 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 70000,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 70000,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_1)

        # 10/01/2021 Uncollected sales (equipment) totaled 5000, with a record cost of equipment of 3000.
        journal_items_3 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 5000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 5000,
        },
        {
            'account_id': self.default_account_type_direct_cost.id,
            'debit': 3000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_stock_delivered.id,
            'debit': 0,
            'credit': 3000,
        }]
        self._init_journal_entry(self.customer_a, datetime(2021, 1, 10, 12, 0), self.default_journal_sale, items=journal_items_3)

        # 20/01/2021 Buy fixed asset 50000 cash
        journal_items_2 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 50000,
        },
        {
            'account_id': self.default_account_fixed_assets.id,
            'debit': 50000,
            'credit': 0,
        }]
        self._init_journal_entry(self.vendor_a, datetime(2021, 1, 20, 12, 0), self.default_journal_purchase, items=journal_items_2)

        # 25/01/2021 Pay a salary 1000
        journal_items_4 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 1000,
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 1000,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 25, 12, 0), self.default_journal_misc, items=journal_items_4)

        # """
        # Line Items                                               | 2021      |
        # ---------------------------------------------------------|-----------|
        # CASH                                                     |           |
        # ---------------------------------------------------------|-----------|
        #   Cash received                                          | 70000     |
        #   Cash spent                                             | -51000    |
        #   Cash surplus                                           | 19000     |
        #   Closing bank balance                                   | 19000     |
        # ---------------------------------------------------------|-----------|
        # PROFITABILITY                                            |           |
        # ---------------------------------------------------------|-----------|
        #   Income                                                 | 5000      |
        #   Cost of Revenue                                        | 3000      |
        #   Gross profit                                           | 2000      |
        #   Expenses                                               | 1000      |
        #   Net Profit                                             | 1000      |
        # ---------------------------------------------------------|-----------|
        # BALANCE SHEET                                            |           |
        # ---------------------------------------------------------|-----------|
        #   Receivables                                            | 5000      |
        #   Payables                                               |           |
        #   Net assets                                             | 71000     |
        # ---------------------------------------------------------|-----------|
        # PERFORMANCE                                              |           |
        # ---------------------------------------------------------|-----------|
        #   Gross profit margin (gross profit / operating income)  | 40        |
        #   Net profit margin (net profit / income)                | 20        |
        #   Return on investments (net profit / assets)            | 1.4       |
        # ---------------------------------------------------------|-----------|
        # POSITION                                                 |           |
        # ---------------------------------------------------------|-----------|
        #   Average debtors days                                   | 364       |
        #   Average creditors days                                 | 0         |
        #   Short term cash forecast                               | 5000      |
        #   Current assets to liabilities                          | 0         |
        # ---------------------------------------------------------|-----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountExecutiveSummary, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                # 1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_01').id,
                'name': 'Cash',
                'columns': {'balance': 0.0, }
            }, {
                # 1.1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_01_01').id,
                'name': 'Cash received',
                'columns': {'balance': 70000, }
            }, {
                # 1.2
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_01_02').id,
                'name': 'Cash spent',
                'columns': {'balance': -51000, }
            }, {
                # 1.3
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_01_03').id,
                'name': 'Cash surplus',
                'columns': {'balance': 19000, }
            }, {
                # 1.4
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_01_04').id,
                'name': 'Closing bank balance',
                'columns': {'balance': 19000, }
            }, {
                # 2
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_02').id,
                'name': 'Profitability',
                'columns': {'balance': 0.0, }
            }, {
                # 2.1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_02_01').id,
                'name': 'Income',
                'columns': {'balance': 5000.0, }
            }, {
                # 2.2
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_02_02').id,
                'name': 'Cost of Revenue',
                'columns': {'balance': 3000.0, }
            }, {
                # 2.3 = 2.1 - 2.2
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_02_03').id,
                'name': 'Gross profit',
                'columns': {'balance': 2000.0, }
            }, {
                # 2.4
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_02_04').id,
                'name': 'Expenses',
                'columns': {'balance': 1000.0, }
            }, {
                # 2.5 = 2.3 - 2.4
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_02_05').id,
                'name': 'Net Profit',
                'columns': {'balance': 1000.0, }
            }, {
                # 3
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_03').id,
                'name': 'Balance Sheet',
                'columns': {'balance': 0.0, }
            }, {
                # 3.1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_03_01').id,
                'name': 'Receivables',
                'columns': {'balance': 5000.0, }
            }, {
                # 3.2
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_03_02').id,
                'name': 'Payables',
                'columns': {'balance': 0.0, }
            }, {
                # 3.3 = 1.3 - 2.5
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_03_03').id,
                'name': 'Net assets',
                'columns': {'balance': 71000, }
            }, {
                # 4
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_04').id,
                'name': 'Performance',
                'columns': {'balance': 0.0, }
            }, {
                # 4.1 = 2.3 / 2.1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_04_01').id,
                'name': 'Gross profit margin (gross profit / operating income)',
                'columns': {'balance': 40, }
            }, {
                # 4.2 = 2.5 / 2.1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_04_02').id,
                'name': 'Net profit margin (net profit / income)',
                'columns': {'balance': 20, }
            }, {
                # 4.3 = 2.5 / 3.3
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_04_03').id,
                'name': 'Return on investments (net profit / assets)',
                'columns': {'balance': 1.4, }
            }, {
                # 5
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_05').id,
                'name': 'Position',
                'columns': {'balance': 0.0, }
            }, {
                # 5.1
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_05_01').id,
                'name': 'Average debtors days',
                'columns': {'balance': 364, }
            }, {
                # 5.2
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_05_02').id,
                'name': 'Average creditors days',
                'columns': {'balance': 0.0, }
            }, {
                # 5.3
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_05_03').id,
                'name': 'Short term cash forecast',
                'columns': {'balance': 5000.0, }
            }, {
                # 5.4
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.executive_summary_line_05_04').id,
                'name': 'Current assets to liabilities',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
