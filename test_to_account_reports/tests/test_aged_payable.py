from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo.tests.common import tagged
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class AgedPayable(AccountReportsCommon):

    def setUp(self):
        super(AgedPayable, self).setUp()
        self.AccountAgedPayable = self.env.ref('to_account_reports.aged_payable_report')

    def test_01_validate_aged_payable(self):
        # 13/08/2021: Create vendor bill 10 for vendor a
        bill_date = date(2021, 8, 13)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            bill = self.init_invoice("in_invoice", self.vendor_a, "2021-08-13", post=True, amounts=[10], taxes=[])
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Vendor A        | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 13, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 10, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }, {
                'id': f'~res.partner~{self.vendor_a.id}',
                'name': 'Vendor A',
                'columns': {'period0': 10, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 0           | 10     | 0       | 0       | 0        | 0     | 10    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Vendor A        | 0           | 10     | 0       | 0       | 0        | 0     | 10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 30, 12, 0), filter_option='custom', date_to=datetime(2021, 8, 30, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 0, 'period1': 10, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }, {
                'id': f'~res.partner~{self.vendor_a.id}',
                'name': 'Vendor A',
                'columns': {'period0': 0, 'period1': 10, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 13/08/2021 Create vendor payment 5 for vendor a
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=bill.ids).create({
            'payment_date': date(2021, 8, 13),
            'journal_id': self.default_journal_bank.id,
            'amount': 5,
        })._create_payments()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 5           | 0      | 0       | 0       | 0        | 0     | 5     |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Vendor A        | 5           | 0      | 0       | 0       | 0        | 0     | 5     |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 13, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 5, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 5}
            }, {
                'id': f'~res.partner~{self.vendor_a.id}',
                'name': 'Vendor A',
                'columns': {'period0': 5, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 5}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

    def test_02_validate_aged_payable(self):
        # 13/08/2021 Create vendor bill 20 for vendor a
        # Payment terms: Now, pay 10. After 45 days, pay 10

        bill_date = date(2021, 8, 13)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[10], taxes=[])

        bill_date += relativedelta(days=45)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[10], taxes=[])

        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Vendor A        | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 13, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 10, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }, {
                'id': f'~res.partner~{self.vendor_a.id}',
                'name': 'Vendor A',
                'columns': {'period0': 10, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Vendor A        | 10          | 0      | 10       | 0       | 0        | 0     | 20    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 10          | 0      | 10       | 0       | 0        | 0     | 20    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 9, 27, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 10, 'period1': 0, 'period2': 10, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 20}
            }, {
                'id': f'~res.partner~{self.vendor_a.id}',
                'name': 'Vendor A',
                'columns': {'period0': 10, 'period1': 0, 'period2': 10, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 20}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
