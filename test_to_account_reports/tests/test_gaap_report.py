from datetime import datetime, date
from odoo.tests.common import tagged
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class GAAPReport(AccountReportsCommon):

    def setUp(self):
        super(GAAPReport, self).setUp()
        self.AccountBalanceSheetReport = self.env.ref('to_account_reports.balance_sheet_report')
        self.AccountProfitLossReport = self.env.ref('to_account_reports.profit_and_loss_report')
        self.AccountCashFlowReport = self.env.ref('to_account_reports.cash_flow_report')

    def test_01_validate_gaap_report(self):
        # Configure the account
        self.default_account_receivable.tag_ids = self.env.ref('account.account_tag_operating')
        self.default_account_payable.tag_ids = self.env.ref('account.account_tag_operating')
        self.default_account_current_liabilities.tag_ids = self.env.ref('account.account_tag_financing')

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

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |    70.000 |
        # Current Assets                            |    70.000 |
        #   Bank and Cash Accounts                  |    70.000 |
        #   Receivables                             |           |
        #   Current Assets                          |           |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |           |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |           |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |           |
        #   Current Liabilities                     |           |
        #   Payables                                |           |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |     70.000|
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |     70.000|
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |     70.000|
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     70.000|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |           |
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |           |
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     70.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     70.000|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 70000.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Buy fixed asset 50000 cash
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
        self._init_journal_entry(self.vendor_a, datetime(2021, 1, 1, 12, 0), self.default_journal_purchase, items=journal_items_2)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |    70.000 |
        # Current Assets                            |    20.000 |
        #   Bank and Cash Accounts                  |    20.000 |
        #   Receivables                             |           |
        #   Current Assets                          |           |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |           |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |           |
        #   Current Liabilities                     |           |
        #   Payables                                |           |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |     70.000|
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |     70.000|
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |     70.000|
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |           |
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |           |
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 20000.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Create vendor bill 9000 for vendor a
        journal_items_3 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 9000,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 9000,
            'credit': 0,
        }]
        self._init_journal_entry(self.vendor_a, datetime(2021, 1, 1, 12, 0), self.default_journal_purchase, items=journal_items_3)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |    79.000 |
        # Current Assets                            |    29.000 |
        #   Bank and Cash Accounts                  |    20.000 |
        #   Receivables                             |           |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |     9.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |     9.000 |
        #   Current Liabilities                     |           |
        #   Payables                                |     9.000 |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    70.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    70.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |    79.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 79000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 29000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 79000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |           |
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |           |
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 20000.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Create vendor payment 5000 for vendor a
        journal_items_4 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 5000,
            'date_maturity': date(2021, 1, 1),
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 5000,
            'credit': 0,
            'date_maturity': date(2021, 1, 1),
            'partner_id': self.vendor_a.id,
        }]
        self._init_journal_entry(self.vendor_a, datetime(2021, 1, 1, 12, 0), self.default_journal_cash, items=journal_items_4)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |    74.000 |
        # Current Assets                            |    24.000 |
        #   Bank and Cash Accounts                  |    15.000 |
        #   Receivables                             |           |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |     4.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |     4.000 |
        #   Current Liabilities                     |           |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    70.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    70.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |    74.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 74000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 24000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 15000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 74000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     15.000|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -5.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |           |
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     15.000|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 15000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 15000.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Create customer payment 250 for customer a
        journal_items_5 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 0,
            'credit': 250,
            'date_maturity': date(2021, 1, 1),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 250,
            'credit': 0,
            'date_maturity': date(2021, 1, 1),
        }]
        self._init_journal_entry(self.customer_a, datetime(2021, 1, 1, 12, 0), self.default_journal_cash, items=journal_items_5)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |    74.000 |
        # Current Assets                            |    24.000 |
        #   Bank and Cash Accounts                  |    15.250 |
        #   Receivables                             |      -250 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |     4.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |     4.000 |
        #   Current Liabilities                     |           |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    70.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    70.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |    74.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 74000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 24000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 15250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': -250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 74000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     15.250|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     15.250|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 15250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 15250.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Short-term bank loan 30000 for 12 months
        journal_items_6 = [{
            'account_id': self.default_account_current_liabilities.id,
            'debit': 0,
            'credit': 30000,
        },
        {
            'account_id': self.default_account_bank.id,
            'debit': 30000,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_6)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   104.000 |
        # Current Assets                            |    54.000 |
        #   Bank and Cash Accounts                  |    45.250 |
        #   Receivables                             |      -250 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |    34.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    34.000 |
        #   Current Liabilities                     |    30.000 |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    70.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    70.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   104.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 54000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 45250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': -250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 34000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 34000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 30000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     45.250|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     30.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     45.250|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 45250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 30000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 30000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 45250.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Long-term bank loan 30000 for 36 months
        journal_items_7 = [{
            'account_id': self.default_account_current_liabilities.id,
            'debit': 0.0,
            'credit': 30000,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 30000,
            'credit': 0.0,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_7)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   134.000 |
        # Current Assets                            |    54.000 |
        #   Bank and Cash Accounts                  |    45.250 |
        #   Receivables                             |      -250 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |    34.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    34.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |   -26.000 |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    70.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    70.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   104.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 134000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 84000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 75250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': -250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 134000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     75.250|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     75.250|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 75250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 75250.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 To increase capital by selling shares 15000
        journal_items_8 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 15000,
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 15000,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_8)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   149.000 |
        # Current Assets                            |    99.000 |
        #   Bank and Cash Accounts                  |    75.250 |
        #   Receivables                             |    14.750 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |           |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |    64.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    64.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |    -4.000 |
        # Plus Non-current Liabilities              |           |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    85.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    85.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   149.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 149000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 99000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 75250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 14750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 149000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     75.250|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     20.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -50.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     75.250|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 75250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 20000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 75250.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Buy technical know-how for 50000, prepayment for 10000, and debt for 40000 over a 48-month period.
        journal_items_9 = [{
            'account_id': self.default_account_non_assets.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_bank.id,
            'debit': 0,
            'credit': 10000,
        },
        {
            'account_id': self.default_account_non_current_liabilities.id,
            'debit': 0,
            'credit': 40000,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_9)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   189.000 |
        # Current Assets                            |    89.000 |
        #   Bank and Cash Accounts                  |    65.250 |
        #   Receivables                             |    14.750 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |    50.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |   104.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    64.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |    40.000 |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    85.000 |
        #   Unallocated Earnings                    |           |
        #     Current Year Unallocated Earnings     |           |
        #       Current Year Earnings               |           |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    85.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   189.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 189000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 89000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 65250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 14750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 50000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 189000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     65.250|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     10.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -60.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     65.250|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 65250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 65250.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Allocate the cost of employing technical know-how over a five-year period, at a rate of 10000 each year.
        journal_items_10 = [{
            'account_id': self.default_account_expense.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_non_assets.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_10)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   179.000 |
        # Current Assets                            |    89.000 |
        #   Bank and Cash Accounts                  |    65.250 |
        #   Receivables                             |    14.750 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |           |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |    40.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |   104.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    64.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |    40.000 |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    75.000 |
        #   Unallocated Earnings                    |   -10.000 |
        #     Current Year Unallocated Earnings     |   -10.000 |
        #       Current Year Earnings               |   -10.000 |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    85.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   179.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 179000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 89000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 65250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 14750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 75000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': -10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': -10000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': -10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 179000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------------|
        # |Expect value (Profit and Loss)|
        # |------------------------------|
        # Line items                    | 2021     |
        # ------------------------------|----------|
        # Net Profit                    |  -10.000 |
        # ------------------------------|----------|
        # Income                        |          |
        #   Gross Profit                |          |
        #       Operating Income        |          |
        #       Deduction Income        |          |
        #       Cost of Revenue         |          |
        #   Other Income                |          |
        # ------------------------------|----------|
        # Expenses                      |   10.000 |
        # ------------------------------|----------|
        #   Expenses                    |   10.000 |
        #   Depreciation                |          |
        # ------------------------------|----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_01').id,
                'name': 'Net Profit',
                'columns': {'balance': -10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02').id,
                'name': 'Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01').id,
                'name': 'Gross Profit',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_01').id,
                'name': 'Operating Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_02').id,
                'name': 'Deduction Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_03').id,
                'name': 'Cost of Revenue',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_02').id,
                'name': 'Other Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03').id,
                'name': 'Expenses',
                'columns': {'balance': 10000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03_01').id,
                'name': 'Expenses',
                'columns': {'balance': 10000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03_02').id,
                'name': 'Depreciation',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     65.250|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |     60.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |     10.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -60.000|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     65.250|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 65250.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 65250.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 1200 for a one-year internet payment
        journal_items_11 = [{
            'account_id': self.default_account_prepayments.id,
            'debit': 1200,
            'credit': 0,
        },
        {
            'account_id': self.default_account_bank.id,
            'debit': 0,
            'credit': 1200,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_11)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   179.000 |
        # Current Assets                            |    89.000 |
        #   Bank and Cash Accounts                  |    64.050 |
        #   Receivables                             |    14.750 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |     1.200 |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |    40.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |   104.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    64.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |    40.000 |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    75.000 |
        #   Unallocated Earnings                    |   -10.000 |
        #     Current Year Unallocated Earnings     |   -10.000 |
        #       Current Year Earnings               |   -10.000 |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    85.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   179.000 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 179000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 89000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 64050.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 14750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 1200.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 75000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': -10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': -10000, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': -10000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 179000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     64.050|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |     60.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |      8.800|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -61.200|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     64.050|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 64050.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 8800.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -61200.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 64050.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 The cost of internet on a monthly basis is 120
        journal_items_12 = [{
            'account_id': self.default_account_expense.id,
            'debit': 120,
            'credit': 0,
        },
        {
            'account_id': self.default_account_prepayments.id,
            'debit': 0,
            'credit': 120,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_12)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   188.000 |
        # Current Assets                            |    88.880 |
        #   Bank and Cash Accounts                  |    64.050 |
        #   Receivables                             |    14.750 |
        #   Current Assets                          |     9.000 |
        #   Prepayments                             |     1.080 |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |    40.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |   104.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    64.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |    40.000 |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    74.880 |
        #   Unallocated Earnings                    |   -10.120 |
        #     Current Year Unallocated Earnings     |   -10.120 |
        #       Current Year Earnings               |   -10.120 |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    85.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   178.880 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 178880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 88880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 64050.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 14750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 9000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 1080.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 74880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': -10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': -10120, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': -10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 178880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------------|
        # |Expect value (Profit and Loss)|
        # |------------------------------|
        # Line items                    | 2021     |
        # ------------------------------|----------|
        # Net Profit                    |  -10.120 |
        # ------------------------------|----------|
        # Income                        |          |
        #   Gross Profit                |          |
        #       Operating Income        |          |
        #       Deduction Income        |          |
        #       Cost of Revenue         |          |
        #   Other Income                |          |
        # ------------------------------|----------|
        # Expenses                      |   10.120 |
        # ------------------------------|----------|
        #   Expenses                    |   10.120 |
        #   Depreciation                |          |
        # ------------------------------|----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_01').id,
                'name': 'Net Profit',
                'columns': {'balance': -10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02').id,
                'name': 'Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01').id,
                'name': 'Gross Profit',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_01').id,
                'name': 'Operating Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_02').id,
                'name': 'Deduction Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_03').id,
                'name': 'Cost of Revenue',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_02').id,
                'name': 'Other Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03').id,
                'name': 'Expenses',
                'columns': {'balance': 10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03_01').id,
                'name': 'Expenses',
                'columns': {'balance': 10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03_02').id,
                'name': 'Depreciation',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     64.050|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |     60.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |      8.800|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -61.200|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     64.050|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 64050.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 8800.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -61200.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 64050.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Uncollected sales (equipment) totaled 5000, with a record cost of equipment of 3000.
        journal_items_13 = [{
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
        self._init_journal_entry(self.customer_a, datetime(2021, 1, 1, 12, 0), self.default_journal_sale, items=journal_items_13)

        # |----------------------------|
        # |Expect value (Balance Sheet)|
        # |----------------------------|
        # Line items                                | As of today |
        # ------------------------------------------|-----------|
        # ASSETS                                    |   180.880 |
        # Current Assets                            |    90.880 |
        #   Bank and Cash Accounts                  |    64.050 |
        #   Receivables                             |    19.750 |
        #   Current Assets                          |     6.000 |
        #   Prepayments                             |     1.080 |
        # Plus Fixed Assets                         |    50.000 |
        # Plus Non-current Assets                   |    40.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES                               |   104.000 |
        # ------------------------------------------|-----------|
        # Current Liabilities                       |    64.000 |
        #   Current Liabilities                     |    60.000 |
        #   Payables                                |     4.000 |
        # Plus Non-current Liabilities              |    40.000 |
        # ------------------------------------------|-----------|
        # EQUITY                                    |    76.880 |
        #   Unallocated Earnings                    |    -8.120 |
        #     Current Year Unallocated Earnings     |    -8.120 |
        #       Current Year Earnings               |    -8.120 |
        #       Current Year Allocated Earnings     |           |
        #     Previous Years Unallocated Earnings   |           |
        #   Retained Earnings                       |    85.000 |
        # ------------------------------------------|-----------|
        # LIABILITIES + EQUITY                      |   180.880 |
        # OFF BALANCE SHEET                         |           |
        # ------------------------------------------|-----------|

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01').id,
                'name': 'ASSETS',
                'columns': {'balance': 180880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01').id,
                'name': 'Current Assets',
                'columns': {'balance': 90880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_01').id,
                'name': 'Bank and Cash Accounts',
                'columns': {'balance': 64050.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_02').id,
                'name': 'Receivables',
                'columns': {'balance': 19750.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_03').id,
                'name': 'Current Assets',
                'columns': {'balance': 6000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_01_04').id,
                'name': 'Prepayments',
                'columns': {'balance': 1080.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_02').id,
                'name': 'Plus Fixed Assets',
                'columns': {'balance': 50000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_01_03').id,
                'name': 'Plus Non-current Assets',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02').id,
                'name': 'LIABILITIES',
                'columns': {'balance': 104000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 64000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_01').id,
                'name': 'Current Liabilities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_01_02').id,
                'name': 'Payables',
                'columns': {'balance': 4000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_02_02').id,
                'name': 'Plus Non-current Liabilities',
                'columns': {'balance': 40000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03').id,
                'name': 'EQUITY',
                'columns': {'balance': 76880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01').id,
                'name': 'Unallocated Earnings',
                'columns': {'balance': -8120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01').id,
                'name': 'Current Year Unallocated Earnings',
                'columns': {'balance': -8120, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_01').id,
                'name': 'Current Year Earnings',
                'columns': {'balance': -8120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_01_02').id,
                'name': 'Current Year Allocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_01_02').id,
                'name': 'Previous Years Unallocated Earnings',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_03_02').id,
                'name': 'Retained Earnings',
                'columns': {'balance': 85000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_04').id,
                'name': 'LIABILITIES + EQUITY',
                'columns': {'balance': 180880.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.balance_sheet_line_05').id,
                'name': 'OFF BALANCE SHEET ACCOUNTS',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------------|
        # |Expect value (Profit and Loss)|
        # |------------------------------|
        # Line items                    | 2021     |
        # ------------------------------|----------|
        # Net Profit                    |   -8.120 |
        # ------------------------------|----------|
        # Income                        |    5.000 |
        #   Gross Profit                |    2.000 |
        #       Operating Income        |    5.000 |
        #       Deduction Income        |          |
        #       Cost of Revenue         |    3.000 |
        #   Other Income                |          |
        # ------------------------------|----------|
        # Expenses                      |   10.120 |
        # ------------------------------|----------|
        #   Expenses                    |   10.120 |
        #   Depreciation                |          |
        # ------------------------------|----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_01').id,
                'name': 'Net Profit',
                'columns': {'balance': -8120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02').id,
                'name': 'Income',
                'columns': {'balance': 5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01').id,
                'name': 'Gross Profit',
                'columns': {'balance': 2000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_01').id,
                'name': 'Operating Income',
                'columns': {'balance': 5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_02').id,
                'name': 'Deduction Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_01_03').id,
                'name': 'Cost of Revenue',
                'columns': {'balance': 3000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_02_02').id,
                'name': 'Other Income',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03').id,
                'name': 'Expenses',
                'columns': {'balance': 10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03_01').id,
                'name': 'Expenses',
                'columns': {'balance': 10120.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.profit_and_loss_line_03_02').id,
                'name': 'Depreciation',
                'columns': {'balance': 0.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     64.050|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |     60.000|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.000|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |      8.800|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -61.200|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     64.050|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 64050.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 8800.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -61200.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 64050.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Interest on the exchange rate 28
        journal_items_14 = [{
            'account_id': self.default_account_bank.id,
            'debit': 28,
            'credit': 0,
        },
        {
            'account_id': self.default_account_foreign.id,
            'debit': 0,
            'credit': 28,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_14)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     64.078|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |     60.028|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.028|
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |      8.800|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -61.200|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     64.078|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 64078.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 60028.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60028.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 8800.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -61200.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 64078.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 Loss of exchange rate 39
        journal_items_15 = [{
            'account_id': self.default_account_foreign.id,
            'debit': 39,
            'credit': 0,
        },
        {
            'account_id': self.default_account_bank.id,
            'debit': 0,
            'credit': 39,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_15)

        # """
        # |------------------------|
        # |Expect value (Cash Flow)|
        # |------------------------|
        # Line Items                                                                    | 2021      |
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, beginning of period                                |           |
        # ------------------------------------------------------------------------------|-----------|
        # Net increase in cash and cash equivalents                                     |     64.039|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from operating activities                                        |     -4.750|
        # ------------------------------------------------------------------------------|-----------|
        #     Advance Payments received from customers                                  |        250|
        #     Cash received from operating activities                                   |           |
        #     Advance payments made to suppliers                                        |     -5.000|
        #     Cash paid for operating activities                                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from investing & extraordinary activities                        |           |
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |           |
        #     Cash out                                                                  |           |
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from financing activities                                        |     59.989|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     60.028|
        #     Cash out                                                                  |        -39|
        # ------------------------------------------------------------------------------|-----------|
        #   Cash flows from unclassified activities                                     |      8.800|
        # ------------------------------------------------------------------------------|-----------|
        #     Cash in                                                                   |     70.000|
        #     Cash out                                                                  |    -61.200|
        # ------------------------------------------------------------------------------|-----------|
        # Cash and cash equivalents, closing balance                                    |     64.039|
        # ------------------------------------------------------------------------------|-----------|
        # """

        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_01').id,
                'name': 'Cash and cash equivalents, beginning of period',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02').id,
                'name': 'Net increase in cash and cash equivalents',
                'columns': {'balance': 64039, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01').id,
                'name': 'Cash flows from operating activities',
                'columns': {'balance': -4750, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_01').id,
                'name': 'Advance Payments received from customers',
                'columns': {'balance': 250, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_02').id,
                'name': 'Cash received from operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_03').id,
                'name': 'Advance payments made to suppliers',
                'columns': {'balance': -5000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_01_04').id,
                'name': 'Cash paid for operating activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02').id,
                'name': 'Cash flows from investing & extraordinary activities',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_01').id,
                'name': 'Cash in',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_02_02').id,
                'name': 'Cash out',
                'columns': {'balance': 0.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03').id,
                'name': 'Cash flows from financing activities',
                'columns': {'balance': 59989.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_01').id,
                'name': 'Cash in',
                'columns': {'balance': 60028.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_03_02').id,
                'name': 'Cash out',
                'columns': {'balance': -39.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04').id,
                'name': 'Cash flows from unclassified activities',
                'columns': {'balance': 8800.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_01').id,
                'name': 'Cash in',
                'columns': {'balance': 70000.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_02_04_02').id,
                'name': 'Cash out',
                'columns': {'balance': -61200.0, }
            }, {
                'id': '~account.report.line~%s' % self.env.ref('to_account_reports.cash_flow_line_03').id,
                'name': 'Cash and cash equivalents, closing balance',
                'columns': {'balance': 64039.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
