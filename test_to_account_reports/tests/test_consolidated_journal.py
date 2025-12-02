# from datetime import datetime, date
# from odoo.tests.common import tagged
# from .common import Common
#
#
# @tagged('post_install', '-at_install')
# class ConsolidatedJournal(Common):
#
#     def setUp(self):
#         super(ConsolidatedJournal, self).setUp()
#         self.AccountConsolidatedJournal = self.env['account.report']
#
#     def test_01_validate_consolidated_journal(self):
#         # 17/08/2021 Create vendor bill 10 for vendor a
#         journal_items_1 = [{
#             'account_id': self.default_account_payable.id,
#             'debit': 0,
#             'credit': 10,
#             'date_maturity': date(2021, 8, 17),
#         },
#         {
#             'account_id': self.default_account_expense.id,
#             'debit': 10,
#             'credit': 0,
#             'date_maturity': date(2021, 8, 17),
#         }]
#         self._init_journal_entry(self.vendor_a, datetime(2021, 8, 17, 12, 0), self.default_journal_purchase, items=journal_items_1)
#         # """
#         # |------------|
#         # |Expect value|
#         # |------------|
#         #
#         # Journal Name (Code)   | Debit | Credit | Balance |
#         # ----------------------|-------|--------|---------|
#         # Vendor Bills (BILL)   | 10    | 10     | 0       |
#         # ----------------------|-------|--------|---------|
#         # Total                 | 10    | 10     | 0       |
#         # ----------------------|-------|--------|---------|
#         # Details per month     |       |        |         |
#         #     Aug 2021          | 10    | 10     | 0       |
#         # """
#         lines = self._get_lines_report(self.AccountConsolidatedJournal, datetime(2021, 8, 17, 12, 0), 'this_year')
#         table_value = [
#             ('Vendor Bills (BILL)', 10, 10, 0),
#             ('Total', 10, 10, 0),
#             ('Details per month', 0, 0, 0),
#             ('Aug 2021', 10, 10, 0),
#         ]
#         self._check_report_value(lines, table_value)
#
#         # Create vendor bill 20 for vendor b
#         journal_items_2 = [{
#             'account_id': self.default_account_payable.id,
#             'debit': 0,
#             'credit': 20,
#             'date_maturity': date(2021, 8, 17),
#         },
#         {
#             'account_id': self.default_account_expense.id,
#             'debit': 20,
#             'credit': 0,
#             'date_maturity': date(2021, 8, 17),
#         }]
#         self._init_journal_entry(self.vendor_b, datetime(2021, 8, 17, 12, 0), self.default_journal_purchase, items=journal_items_2)
#         # """
#         # |------------|
#         # |Expect value|
#         # |------------|
#         #
#         # Journal Name (Code)   | Debit | Credit | Balance |
#         # ----------------------|-------|--------|---------|
#         # Vendor Bills (BILL)   | 30    | 30     | 0       |
#         # ----------------------|-------|--------|---------|
#         # Total                 | 30    | 30     | 0       |
#         # ----------------------|-------|--------|---------|
#         # Details per month     |       |        |         |
#         #     Aug 2021          | 30    | 30     | 0       |
#         # """
#         lines = self._get_lines_report(self.AccountConsolidatedJournal, datetime(2021, 8, 17, 12, 0), 'this_year')
#         table_value = [
#             ('Vendor Bills (BILL)', 30, 30, 0),
#             ('Total', 30, 30, 0),
#             ('Details per month', 0, 0, 0),
#             ('Aug 2021', 30, 30, 0),
#         ]
#         self._check_report_value(lines, table_value)
#
#     def test_02_validate_consolidated_journal(self):
#         # Create vendor payment 50 for vendor a
#         journal_items_1 = [{
#             'account_id': self.default_account_bank.id,
#             'debit': 0,
#             'credit': 50,
#             'date_maturity': date(2021, 8, 17),
#         },
#         {
#             'account_id': self.default_account_payable.id,
#             'debit': 50,
#             'credit': 0,
#             'date_maturity': date(2021, 8, 17),
#         }]
#         self._init_journal_entry(self.vendor_a, datetime(2021, 8, 17, 12, 0), self.default_journal_bank, items=journal_items_1)
#         # """
#         # |------------|
#         # |Expect value|
#         # |------------|
#         #
#         # Journal Name (Code)   | Debit | Credit | Balance |
#         # ----------------------|-------|--------|---------|
#         # Bank (BNK1)           | 50    | 50     | 0       |
#         # ----------------------|-------|--------|---------|
#         # Total                 | 50    | 50     | 0       |
#         # ----------------------|-------|--------|---------|
#         # Details per month     |       |        |         |
#         #     Aug 2021          | 50    | 50     | 0       |
#         # """
#         lines = self._get_lines_report(self.AccountConsolidatedJournal, datetime(2021, 8, 17, 12, 0), 'this_year')
#         table_value = [
#             ('Bank (BNK1)', 50, 50, 0),
#             ('Total', 50, 50, 0),
#             ('Details per month', 0, 0, 0),
#             ('Aug 2021', 50, 50, 0),
#         ]
#         self._check_report_value(lines, table_value)
