from datetime import datetime, date
from odoo.tests.common import tagged
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class TrialBalance(AccountReportsCommon):

    def setUp(self):
        super(TrialBalance, self).setUp()
        self.AccountTrialBalance = self.env.ref('to_account_reports.trial_balance_report')

    def test_01_validate_trial_balance(self):
        # 12/08/2020 Capital contribution 100 cash
        journal_items_1 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 100,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 100,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2020, 8, 12, 12, 0), self.default_journal_misc, items=journal_items_1)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name           | Initial Balance |   Period Time   |      Total      |
        #         |                | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|--------------- |--------|--------|--------|--------|--------|--------|
        #  101501 | Cash           | 100    |        |        |        | 100    |        |
        #  301000 | Capital        |        | 100    |        |        |        | 100    |
        # --------|----------------|-----------------|--------|--------|--------|--------|
        #         | Total          | 100    | 100    |        |        | 100    | 100    |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 100.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 100.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 100.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 100.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 100.0, 'end_balance_credit': 100.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 12/08/2020 Capital contribution 700 bank
        journal_items_2 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 700,
        },
        {
            'account_id': self.default_account_bank.id,
            'debit': 700,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2020, 8, 12, 12, 0), self.default_journal_misc, items=journal_items_2)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name           | Initial Balance |   Period Time   |      Total      |
        #         |                | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|--------------- |--------|--------|--------|--------|--------|--------|
        #  101401 | Bank           | 700    |        |        |        | 700    |        |
        #  101501 | Cash           | 100    |        |        |        | 100    |        |
        #  301000 | Capital        |        | 800    |        |        |        | 800    |
        # --------|----------------|-----------------|--------|--------|--------|--------|
        #         | Total          | 800    | 800    |        |        | 800    | 800    |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 100.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 800.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 800.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 800.0, 'end_balance_credit': 800.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 12/08/2020 Create vendor bill 500 for vendor a
        journal_items_3 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 500,
            'date_maturity': date(2020, 8, 12),
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 500,
            'credit': 0,
            'date_maturity': date(2020, 8, 12),
        }]
        self._init_journal_entry(self.vendor_a, datetime(2020, 8, 12, 12, 0), self.default_journal_purchase, items=journal_items_3)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name                          | Initial Balance |   Period Time   |      Total      |
        #         |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|-------------------------------|--------|--------|--------|--------|--------|--------|
        #  101401 | Bank                          | 700    |        |        |        | 700    |        |
        #  101501 | Cash                          | 100    |        |        |        | 100    |        |
        #  211000 | Account Payable               |        | 500    |        |        |        | 500    |
        #  301000 | Capital                       |        | 800    |        |        |        | 800    |
        #  600000 | Expenses                      | 500    |        |        |        | 500    |        |
        # --------|-------------------------------|-----------------|--------|--------|--------|--------|
        #         | Total                         | 1300   | 1300   |        |        | 1300   | 1300   |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 100.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_payable.id}',
                'name': self.default_account_payable.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 500.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 500.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 800.0},
            },
            {
                'id': f'~account.account~{self.balancing_account.id}',
                'name': self.balancing_account.display_name,
                'columns': {'initial_balance_debit': 500.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 500.0, 'end_balance_credit': 0.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 1300.0, 'initial_balance_credit': 1300.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 1300.0, 'end_balance_credit': 1300.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 12/08/2020 Create vendor bill 200 for vendor a
        journal_items_4 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 200,
            'date_maturity': date(2020, 8, 12),
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 200,
            'credit': 0,
            'date_maturity': date(2020, 8, 12),
        }]
        self._init_journal_entry(self.vendor_a, datetime(2020, 8, 12, 12, 0), self.default_journal_purchase, items=journal_items_4)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name                          | Initial Balance |   Period Time   |      Total      |
        #         |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|-------------------------------|--------|--------|--------|--------|--------|--------|
        #  101401 | Bank                          | 700    |        |        |        | 700    |        |
        #  101501 | Cash                          | 100    |        |        |        | 100    |        |
        #  110200 | Stock Interim (Received)      | 200    |        |        |        | 200    |        |
        #  211000 | Account Payable               |        | 700    |        |        |        | 700    |
        #  301000 | Capital                       |        | 800    |        |        |        | 800    |
        #  999999 | Undistributed Profits/Losses  | 500    |        |        |        | 500    |        |
        # --------|-------------------------------|-----------------|--------|--------|--------|--------|
        #         | Total                         | 1500   | 1500   |        |        | 1500   | 1500   |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 100.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_stock.id}',
                'name': self.default_account_stock.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_payable.id}',
                'name': self.default_account_payable.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 700.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 700.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 800.0},
            },
            {
                'id': f'~account.account~{self.balancing_account.id}',
                'name': self.balancing_account.display_name,
                'columns': {'initial_balance_debit': 500.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 500.0, 'end_balance_credit': 0.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 1500.0, 'initial_balance_credit': 1500.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 1500.0, 'end_balance_credit': 1500.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 12/08/2020 Create customer invoice 200 for customer a
        journal_items_5 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 200,
            'date_maturity': date(2020, 8, 12),
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 200,
            'credit': 0,
            'date_maturity': date(2020, 8, 12),
        }]
        self._init_journal_entry(self.customer_a, datetime(2020, 8, 12, 12, 0), self.default_journal_sale, items=journal_items_5)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name                          | Initial Balance |   Period Time   |      Total      |
        #         |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|-------------------------------|--------|--------|--------|--------|--------|--------|
        #  101401 | Bank                          | 700    |        |        |        | 700    |        |
        #  101501 | Cash                          | 100    |        |        |        | 100    |        |
        #  110200 | Stock Interim (Received)      | 200    |        |        |        | 200    |        |
        #  110200 | Account Receivable            | 200    |        |        |        | 200    |        |
        #  211000 | Account Payable               |        | 700    |        |        |        | 700    |
        #  301000 | Capital                       |        | 800    |        |        |        | 800    |
        #  999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        # --------|-------------------------------|-----------------|--------|--------|--------|--------|
        #         | Total                         | 1500   | 1500   |        |        | 1500   | 1500   |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 100.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_stock.id}',
                'name': self.default_account_stock.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_receivable.id}',
                'name': self.default_account_receivable.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_payable.id}',
                'name': self.default_account_payable.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 700.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 700.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 800.0},
            },
            {
                'id': f'~account.account~{self.balancing_account.id}',
                'name': self.balancing_account.display_name,
                'columns': {'initial_balance_debit': 300.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 300.0, 'end_balance_credit': 0.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 1500.0, 'initial_balance_credit': 1500.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 1500.0, 'end_balance_credit': 1500.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 05/01/2021 Capital contribution 500 cash
        journal_items_6 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 500,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 500,
            'credit': 0,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 5, 12, 0), self.default_journal_misc, items=journal_items_6)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name                          | Initial Balance |   Period Time   |      Total      |
        #         |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|-------------------------------|--------|--------|--------|--------|--------|--------|
        #  101401 | Bank                          | 700    |        |        |        | 700    |        |
        #  101501 | Cash                          | 100    |        | 500    |        | 600    |        |
        #  110200 | Stock Interim (Received)      | 200    |        |        |        | 200    |        |
        #  110200 | Account Receivable            | 200    |        |        |        | 200    |        |
        #  211000 | Account Payable               |        | 700    |        |        |        | 700    |
        #  301000 | Capital                       |        | 800    |        | 500    |        | 1300   |
        #  999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        # --------|-------------------------------|-----------------|--------|--------|--------|--------|
        #         | Total                         | 1500   | 1500   | 500    | 500    | 2000   | 2000   |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 500.0, 'credit': 0.0, 'end_balance_debit': 600.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_stock.id}',
                'name': self.default_account_stock.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_receivable.id}',
                'name': self.default_account_receivable.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_payable.id}',
                'name': self.default_account_payable.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 700.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 700.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 500.0, 'end_balance_debit': 0.0, 'end_balance_credit': 1300.0},
            },
            {
                'id': f'~account.account~{self.balancing_account.id}',
                'name': self.balancing_account.display_name,
                'columns': {'initial_balance_debit': 300.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 300.0, 'end_balance_credit': 0.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 1500.0, 'initial_balance_credit': 1500.0, 'debit': 500.0, 'credit': 500.0, 'end_balance_debit': 2000.0, 'end_balance_credit': 2000.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 10/02/2020 Create vendor bill 300 for vendor a
        journal_items_7 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 300,
            'date_maturity': date(2021, 2, 10),
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 300,
            'credit': 0,
            'date_maturity': date(2021, 2, 10),
        }]
        self._init_journal_entry(self.vendor_a, datetime(2021, 2, 10, 12, 0), self.default_journal_purchase, items=journal_items_7)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name                          | Initial Balance |   Period Time   |      Total      |
        #         |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|-------------------------------|--------|--------|--------|--------|--------|--------|
        #  101401 | Bank                          | 700    |        |        |        | 700    |        |
        #  101501 | Cash                          | 100    |        | 500    |        | 600    |        |
        #  110200 | Stock Interim (Received)      | 200    |        | 300    |        | 500    |        |
        #  110200 | Account Receivable            | 200    |        |        |        | 200    |        |
        #  211000 | Account Payable               |        | 700    |        | 300    |        | 1000   |
        #  301000 | Capital                       |        | 800    |        | 500    |        | 1300   |
        #  999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        # --------|-------------------------------|-----------------|--------|--------|--------|--------|
        #         | Total                         | 1500   | 1500   | 800    | 800    | 2300   | 2300   |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 100.0, 'initial_balance_credit': 0.0, 'debit': 500.0, 'credit': 0.0, 'end_balance_debit': 600.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_stock.id}',
                'name': self.default_account_stock.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 300.0, 'credit': 0.0, 'end_balance_debit': 500.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_receivable.id}',
                'name': self.default_account_receivable.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_payable.id}',
                'name': self.default_account_payable.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 700.0, 'debit': 0.0, 'credit': 300.0, 'end_balance_debit': 0.0, 'end_balance_credit': 1000.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 800.0, 'debit': 0.0, 'credit': 500.0, 'end_balance_debit': 0.0, 'end_balance_credit': 1300.0},
            },
            {
                'id': f'~account.account~{self.balancing_account.id}',
                'name': self.balancing_account.display_name,
                'columns': {'initial_balance_debit': 300.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 300.0, 'end_balance_credit': 0.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 1500.0, 'initial_balance_credit': 1500.0, 'debit': 800.0, 'credit': 800.0, 'end_balance_debit': 2300.0, 'end_balance_credit': 2300.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 13/08/2021 Change accounting period 01/02/2021 - 28/02/2021
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #  Code   | Name                          | Initial Balance |   Period Time   |      Total      |
        #         |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        # --------|-------------------------------|--------|--------|--------|--------|--------|--------|
        #  101401 | Bank                          | 700    |        |        |        | 700    |        |
        #  101501 | Cash                          | 600    |        |        |        | 600    |        |
        #  110200 | Stock Interim (Received)      | 200    |        | 300    |        | 500    |        |
        #  110200 | Account Receivable            | 200    |        |        |        | 200    |        |
        #  211000 | Account Payable               |        | 700    |        | 300    |        | 1000   |
        #  301000 | Capital                       |        | 1300   |        |        |        | 1300   |
        #  999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        # --------|-------------------------------|-----------------|--------|--------|--------|--------|
        #         | Total                         | 2000   | 2000   | 300    | 300    | 2300   | 2300   |
        # """
        lines_to_check = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 2, 1), date(2021, 2, 28))
        lines_expected_value = [{
                'id': f'~account.account~{self.default_account_bank.id}',
                'name': self.default_account_bank.display_name,
                'columns': {'initial_balance_debit': 700.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 700.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_cash.id}',
                'name': self.default_account_cash.display_name,
                'columns': {'initial_balance_debit': 600.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 600.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_stock.id}',
                'name': self.default_account_stock.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 300.0, 'credit': 0.0, 'end_balance_debit': 500.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_receivable.id}',
                'name': self.default_account_receivable.display_name,
                'columns': {'initial_balance_debit': 200.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 200.0, 'end_balance_credit': 0.0},
            },
            {
                'id': f'~account.account~{self.default_account_payable.id}',
                'name': self.default_account_payable.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 700.0, 'debit': 0.0, 'credit': 300.0, 'end_balance_debit': 0.0, 'end_balance_credit': 1000.0},
            },
            {
                'id': f'~account.account~{self.default_account_capital.id}',
                'name': self.default_account_capital.display_name,
                'columns': {'initial_balance_debit': 0.0, 'initial_balance_credit': 1300.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 0.0, 'end_balance_credit': 1300.0},
            },
            {
                'id': f'~account.account~{self.balancing_account.id}',
                'name': self.balancing_account.display_name,
                'columns': {'initial_balance_debit': 300.0, 'initial_balance_credit': 0.0, 'debit': 0.0, 'credit': 0.0, 'end_balance_debit': 300.0, 'end_balance_credit': 0.0},
            },
            {
                'id': '~account.account~total',
                'name': 'Total',
                'columns': {'initial_balance_debit': 2000.0, 'initial_balance_credit': 2000.0, 'debit': 300.0, 'credit': 300.0, 'end_balance_debit': 2300.0, 'end_balance_credit': 2300.0},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
