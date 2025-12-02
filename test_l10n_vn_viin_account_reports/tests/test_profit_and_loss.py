from datetime import datetime
from odoo.tests.common import tagged
from .common import AccountReportL10nVn


@tagged('post_install', '-at_install', 'post_install_l10n')
class ProfitLoss(AccountReportL10nVn):

    def setUp(self):
        super(ProfitLoss, self).setUp()
        self.AccountProfitLossReport = self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_report')

    def test_01_validate_profit_loss(self):
        # 01/01/2021 Uncollected sales (equipment) totaled 100000, with a record cost of equipment of 60000.
        journal_items_1 = [{
            'account_id': self.default_account_131.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 100000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 60000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 0,
            'credit': 60000,
        }]
        self._init_journal_entry(self.customer_a, datetime(2021, 1, 1, 12, 0), self.default_journal_vn_sale, items=journal_items_1)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 100000   |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 40000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      |          |
        #     7. Financial expenses                            | 22   |      |          |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      |          |
        #     9. General administration expenses               | 25   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | 40000    |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | 40000    |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | 40000    |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 40000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': 40000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': 40000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': 40000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 20/01/2021 Due of poor quality, items are sold at a lower price. Debt was reduced by 5,000.
        journal_items_2 = [{
            'account_id': self.default_account_5212.id,
            'debit': 5000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 5000,
        }]
        self._init_journal_entry(self.customer_a, datetime(2021, 1, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_2)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      |          |
        #     7. Financial expenses                            | 22   |      |          |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      |          |
        #     9. General administration expenses               | 25   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | 35000    |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | 35000    |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | 35000    |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': 35000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 17/08/2021 The company deposits 5,000 in the bank and receives a set monthly interest payment to the company's primary account.
        journal_items_3 = [{
            'account_id': self.default_account_1121.id,
            'debit': 5000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_515.id,
            'debit': 0,
            'credit': 5000,
        }]
        self._init_journal_entry(None, datetime(2021, 12, 30, 12, 0), self.default_journal_vn_misc, items=journal_items_3)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      |          |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      |          |
        #     9. General administration expenses               | 25   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | 40000    |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | 40000    |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | 40000    |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': 40000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': 40000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': 40000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 15/08/2021 5000 per month interest on a bank loan
        journal_items_4 = [{
            'account_id': self.default_account_635.id,
            'debit': 5000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 5000,
        }]
        self._init_journal_entry(None, datetime(2021, 8, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_4)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 5000     |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      |          |
        #     9. General administration expenses               | 25   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | 35000    |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | 35000    |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | 35000    |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': 35000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 31/11/2021 Selling trading securities resulted in a loss of 19,000.
        journal_items_5 = [{
            'account_id': self.default_account_635.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 9000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1218.id,
            'debit': 0,
            'credit': 19000,
        }]
        self._init_journal_entry(None, datetime(2021, 11, 30, 12, 0), self.default_journal_vn_misc, items=journal_items_5)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 15000    |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      |          |
        #     9. General administration expenses               | 25   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | 25000    |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | 25000    |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | 25000    |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': 25000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': 25000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': 25000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 31/08/2021 Salespeople's remuneration is 30,000.
        journal_items_6 = [{
            'account_id': self.default_account_6411.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3341.id,
            'debit': 0,
            'credit': 30000,
        }]
        self._init_journal_entry(None, datetime(2021, 8, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_6)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 15000    |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      | 30000    |
        #     9. General administration expenses               | 25   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | -5000    |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | -5000    |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | -5000    |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': -5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': -5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': -5000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 31/08/2021 Management salaries are paid at a rate of 40,000.
        journal_items_7 = [{
            'account_id': self.default_account_6421.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3341.id,
            'debit': 0,
            'credit': 30000,
        }]
        self._init_journal_entry(None, datetime(2021, 8, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_7)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 15000    |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      | 30000    |
        #     9. General administration expenses               | 25   |      | 30000    |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | -35000   |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      |          |
        #     12. Other Expenses                               | 32   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | -35000   |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | -35000   |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': -35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': -35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': -35000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 01/01/2021 For 100,000, you may purchase fixed assets. Depreciation is calculated as follows: 8 months = 80,000.
        journal_items_8 = [{
            'account_id': self.default_account_2112.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 100000,
        },
        {
            'account_id': self.default_account_6421.id,
            'debit': 80000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2141.id,
            'debit': 0,
            'credit': 80000,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_711.id,
            'debit': 0,
            'credit': 50000,
        },
        {
            'account_id': self.default_account_2141.id,
            'debit': 80000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_811.id,
            'debit': 20000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2111.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_8)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 15000    |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      | 30000    |
        #     9. General administration expenses               | 25   |      | 110000   |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | -115000  |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      | 50000    |
        #     12. Other Expenses                               | 32   |      | 20000    |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      | 30000    |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | -85000   |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      |          |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | -85000   |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 110000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': -115000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': -85000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': -85000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 05/01/2021 Calculating the present company income tax liability in order to pay 15,000 in 2020
        journal_items_9 = [{
            'account_id': self.default_account_8211.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3334.id,
            'debit': 0,
            'credit': 15000,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_9)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 15000    |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      | 30000    |
        #     9. General administration expenses               | 25   |      | 110000   |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | -115000  |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      | 50000    |
        #     12. Other Expenses                               | 32   |      | 20000    |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      | 30000    |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | -85000   |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      | 15000    |
        #     16. Deferred corporate income tax expenses       | 52   |      |          |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | -100000  |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 110000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': -115000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': -85000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': -100000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 05/01/2021 Calculation of deferred corporate income tax expenditure for 2020 payment of 4000
        journal_items_10 = [{
            'account_id': self.default_account_8212.id,
            'debit': 4000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_347.id,
            'debit': 0,
            'credit': 4000,
        }]
        self._init_journal_entry(None, datetime(2021, 1, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_10)
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        # Line items                                           | Code | Note |   2021   |
        # -----------------------------------------------------|------|------|----------|
        #     1. Revenues from sales and services rendered     | 01   |      | 100000   |
        #     2. Revenue deductions                            | 02   |      | 5000     |
        # -----------------------------------------------------|------|------|----------|
        # 3. Net revenues from sales and services rendered     | 10   |      | 95000    |
        # (10 = 01 - 02)                                       |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     4. Costs of goods sold                           | 11   |      | 60000    |
        # -----------------------------------------------------|------|------|----------|
        # 5. Gross revenues from sales and services rendered   | 20   |      | 35000    |
        # (20=10-11)                                           |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     6. Financial income                              | 21   |      | 5000     |
        #     7. Financial expenses                            | 22   |      | 15000    |
        #     - In which: Interest expenses                    | 23   |      |          |
        #     8. Selling expenses                              | 24   |      | 30000    |
        #     9. General administration expenses               | 25   |      | 110000   |
        # -----------------------------------------------------|------|------|----------|
        # 10. Net profits from operating activities            | 30   |      | -115000  |
        # 30 = 20 + (21 - 22) - (24 + 25)                      |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        #     11. Other Income                                 | 31   |      | 50000    |
        #     12. Other Expenses                               | 32   |      | 20000    |
        # -----------------------------------------------------|------|------|----------|
        # 13. Other profits (40 = 31 - 32)                     | 40   |      | 30000    |
        # -----------------------------------------------------|------|------|----------|
        # 14. Total net profits before tax (50 = 30 + 40)      | 50   |      | -85000   |
        # -----------------------------------------------------|------|------|----------|
        #     15. Current corporate income tax expenses        | 51   |      | 15000    |
        #     16. Deferred corporate income tax expenses       | 52   |      | 4000     |
        # -----------------------------------------------------|------|------|----------|
        # 17. Profits after enterprise income tax              | 60   |      | -104000  |
        # (60=50 - 51 - 52)                                    |      |      |          |
        # -----------------------------------------------------|------|------|----------|
        # """
        lines_to_check = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 12, 30, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_01').id,
                'name': '1. Revenues from sales and services rendered',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_02').id,
                'name': '2. Revenue deductions',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_03').id,
                'name': '3. Net revenues from sales and services rendered (10 = 01 - 02)',
                'columns': {'balance': 95000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_04').id,
                'name': '4. Costs of goods sold',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_05').id,
                'name': '5. Gross revenues from sales and services rendered (20 = 10 - 11)',
                'columns': {'balance': 35000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_06').id,
                'name': '6. Financial income',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_07').id,
                'name': '7. Financial expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_08').id,
                'name': '- In which: Interest expenses',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_09').id,
                'name': '8. Selling expenses',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_10').id,
                'name': '9. General administration expenses',
                'columns': {'balance': 110000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_11').id,
                'name': '10. Net profits from operating activities 30 = 20 + (21 - 22) - (25 + 26)',
                'columns': {'balance': -115000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_12').id,
                'name': '11. Other Income',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_13').id,
                'name': '12. Other Expenses',
                'columns': {'balance': 20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_14').id,
                'name': '13. Other profits (40 = 31 - 32)',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_15').id,
                'name': '14. Total net profits before tax (50 = 30 + 40)',
                'columns': {'balance': -85000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_16').id,
                'name': '15. Current corporate income tax expenses',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_17').id,
                'name': '16. Deferred corporate income tax expenses',
                'columns': {'balance': 4000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.profit_and_loss_c200_line_18').id,
                'name': '17. Profits after enterprise income tax (60 = 50 - 51 - 52)',
                'columns': {'balance': -104000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
