from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import tagged
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class AgedReceivable(AccountReportsCommon):

    def setUp(self):
        super(AgedReceivable, self).setUp()
        self.AccountAgedReceivable = self.env.ref('to_account_reports.aged_receivable_report')

    def test_01_validate_aged_receivable(self):
        # 13/08/2021 Create customer invoice 10 for customer a
        invoice_date = date(2021, 8, 13)        # 13/08/2021
        with self.patch_datetime_now(invoice_date), self.patch_date_today(invoice_date), self.patch_date_context_today(invoice_date):
            inv = self.init_invoice("out_invoice", self.customer_a, invoice_date, post=True, amounts=[10], taxes=[])

        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Customer A      | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 13, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 10, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }, {
                'id': f'~res.partner~{self.customer_a.id}',
                'name': 'Customer A',
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
        # Customer A      | 0           | 10     | 0       | 0       | 0        | 0     | 10    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 0           | 10     | 0       | 0       | 0        | 0     | 10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 30, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 0, 'period1': 10, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }, {
                'id': f'~res.partner~{self.customer_a.id}',
                'name': 'Customer A',
                'columns': {'period0': 0, 'period1': 10, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # Create customer payment 5 for customer a
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=inv.ids).create({
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
        # Customer A      | 5           | 0      | 0       | 0       | 0        | 0     | 5     |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 5           | 0      | 0       | 0       | 0        | 0     | 5     |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 13, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 5, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 5}
            }, {
                'id': f'~res.partner~{self.customer_a.id}',
                'name': 'Customer A',
                'columns': {'period0': 5, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 5}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

    def test_02_validate_aged_receivable(self):
        # Create customer invoice 20 for customer a
        # Payment terms: Now, pay 10. After 45 days, pay 10
        invoice_date = date(2021, 8, 13)        # 13/08/2021
        with self.patch_datetime_now(invoice_date), self.patch_date_today(invoice_date), self.patch_date_context_today(invoice_date):
            self.init_invoice("out_invoice", self.customer_a, invoice_date, post=True, amounts=[10], taxes=[])

        invoice_date += relativedelta(days=45)  # 27/09/2021
        with self.patch_datetime_now(invoice_date), self.patch_date_today(invoice_date), self.patch_date_context_today(invoice_date):
            self.init_invoice("out_invoice", self.customer_a, invoice_date, post=True, amounts=[10], taxes=[])

        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | At Date     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Customer A      | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 10          | 0      | 0       | 0       | 0        | 0     | 10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 13, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 10, 'period1': 0, 'period2': 0, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 10}
            }, {
                'id': f'~res.partner~{self.customer_a.id}',
                'name': 'Customer A',
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
        # Customer A      | 10          | 0      | 10      | 0       | 0        | 0     | 20    |
        # ----------------|-------------|--------|---------|---------|----------|-------|-------|
        # Total           | 10          | 0      | 10      | 0       | 0        | 0     | 20    |
        # """
        lines_to_check = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 9, 27, 12, 0))
        lines_expected_value = [{
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'period0': 10, 'period1': 0, 'period2': 10, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 20}
            }, {
                'id': f'~res.partner~{self.customer_a.id}',
                'name': 'Customer A',
                'columns': {'period0': 10, 'period1': 0, 'period2': 10, 'period3': 0, 'period4': 0, 'period5': 0, 'total': 20}
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
