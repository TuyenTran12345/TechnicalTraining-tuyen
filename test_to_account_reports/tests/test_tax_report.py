from datetime import datetime, date
from odoo.tests.common import tagged
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class TaxReport(AccountReportsCommon):

    def setUp(self):
        super(TaxReport, self).setUp()
        self.GeneralTaxReport = self.env.ref('account.generic_tax_report')
        self.GeneralTaxReportAccountTax = self.env.ref('account.generic_tax_report_account_tax')
        self.GeneralTaxReportTaxAccount = self.env.ref('account.generic_tax_report_tax_account')

        # Create Bill
        bill_date = date(2024, 8, 1)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            self.bill_001 = self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[100], taxes=[self.tax_price_purchase_10])

        bill_date = date(2024, 8, 2)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            self.bill_002 = self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[150], taxes=[self.tax_price_purchase_5])

        bill_date = date(2024, 8, 3)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            self.bill_003 = self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[50], taxes=[self.tax_price_purchase_5])

        # Create Invoice
        inv_date = date(2024, 8, 4)
        with self.patch_datetime_now(inv_date), self.patch_date_today(inv_date), self.patch_date_context_today(inv_date):
            self.inv_001 = self.init_invoice("out_invoice", self.vendor_a, inv_date, post=True, amounts=[100], taxes=[self.tax_price_sale_5])

        inv_date = date(2024, 8, 5)
        with self.patch_datetime_now(inv_date), self.patch_date_today(inv_date), self.patch_date_context_today(inv_date):
            self.inv_002 = self.init_invoice("out_invoice", self.vendor_a, inv_date, post=True, amounts=[150], taxes=[self.tax_price_sale_10])

    def test_01_validate_tax_report(self):
        # Report General Tax
        lines = self._get_lines_report(self.GeneralTaxReport, datetime(2024, 8, 31, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': '~account.tax.use~purchase',
                'name': 'Purchases',
                'columns': {
                    'net': 300.0, 'tax': 20,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.tax~{self.tax_price_purchase_5.id}',
                'name': self.tax_price_purchase_5.name,
                'columns': {
                    'net': 200.0, 'tax': 10.0,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.tax~{self.tax_price_purchase_10.id}',
                'name': self.tax_price_purchase_10.name,
                'columns': {
                    'net': 100.0, 'tax': 10,
                },
            },
            {
                'id': '~account.tax.use~sale',
                'name': 'Sales',
                'columns': {
                    'net': 250.0, 'tax': 20.0,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.tax~{self.tax_price_sale_5.id}',
                'name': self.tax_price_sale_5.name,
                'columns': {
                    'net': 100.0, 'tax': 5.0,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.tax~{self.tax_price_sale_10.id}',
                'name': self.tax_price_sale_10.name,
                'columns': {
                    'net': 150.0, 'tax': 15,
                },
            }
        ]
        self._check_report_value(lines, lines_expected_value)

        # Report General Tax Account->Tax
        lines = self._get_lines_report(self.GeneralTaxReportAccountTax, datetime(2024, 8, 31, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': '~account.tax.use~purchase',
                'name': 'Purchases',
                'columns': {
                    'net': 300.0, 'tax': 20,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.account~{self.bill_001.invoice_line_ids.account_id.id}',
                'name': self.bill_001.invoice_line_ids.account_id.display_name,
                'columns': {
                    'net': 300.0, 'tax': 20.0,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.account~{self.bill_001.invoice_line_ids.account_id.id}~account.tax~{self.tax_price_purchase_5.id}',
                'name': self.tax_price_purchase_5.name,
                'columns': {
                    'net': 200.0, 'tax': 10.0,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.account~{self.bill_001.invoice_line_ids.account_id.id}~account.tax~{self.tax_price_purchase_10.id}',
                'name': self.tax_price_purchase_10.name,
                'columns': {
                    'net': 100.0, 'tax': 10,
                },
            },
            {
                'id': '~account.tax.use~sale',
                'name': 'Sales',
                'columns': {
                    'net': 250.0, 'tax': 20,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.account~{self.inv_001.invoice_line_ids.account_id.id}',
                'name': self.inv_001.invoice_line_ids.account_id.display_name,
                'columns': {
                    'net': 250.0, 'tax': 20.0,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.account~{self.inv_001.invoice_line_ids.account_id.id}~account.tax~{self.tax_price_sale_5.id}',
                'name': self.tax_price_sale_5.name,
                'columns': {
                    'net': 100.0, 'tax': 5.0,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.account~{self.inv_001.invoice_line_ids.account_id.id}~account.tax~{self.tax_price_sale_10.id}',
                'name': self.tax_price_sale_10.name,
                'columns': {
                    'net': 150.0, 'tax': 15,
                },
            }
        ]
        self._check_report_value(lines, lines_expected_value)

        # Report General Tax Tax->Account
        lines = self._get_lines_report(self.GeneralTaxReportTaxAccount, datetime(2024, 8, 31, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': '~account.tax.use~purchase',
                'name': 'Purchases',
                'columns': {
                    'net': 300.0, 'tax': 20,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.tax~{self.tax_price_purchase_5.id}',
                'name': self.tax_price_purchase_5.name,
                'columns': {
                    'net': 200.0, 'tax': 10,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.tax~{self.tax_price_purchase_5.id}~account.account~{self.bill_001.invoice_line_ids.account_id.id}',
                'name': self.bill_001.invoice_line_ids.account_id.display_name,
                'columns': {
                    'net': 200.0, 'tax': 10.0,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.tax~{self.tax_price_purchase_10.id}',
                'name': self.tax_price_purchase_10.name,
                'columns': {
                    'net': 100.0, 'tax': 10.0,
                },
            },
            {
                'id': f'~account.tax.use~purchase~account.tax~{self.tax_price_purchase_10.id}~account.account~{self.bill_001.invoice_line_ids.account_id.id}',
                'name': self.bill_001.invoice_line_ids.account_id.display_name,
                'columns': {
                    'net': 100.0, 'tax': 10.0,
                },
            },
            {
                'id': '~account.tax.use~sale',
                'name': 'Sales',
                'columns': {
                    'net': 250.0, 'tax': 20,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.tax~{self.tax_price_sale_5.id}',
                'name': self.tax_price_sale_5.name,
                'columns': {
                    'net': 100.0, 'tax': 5.0,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.tax~{self.tax_price_sale_5.id}~account.account~{self.inv_001.invoice_line_ids.account_id.id}',
                'name': self.inv_001.invoice_line_ids.account_id.display_name,
                'columns': {
                    'net': 100.0, 'tax': 5.0,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.tax~{self.tax_price_sale_10.id}',
                'name': self.tax_price_sale_10.name,
                'columns': {
                    'net': 150.0, 'tax': 15,
                },
            },
            {
                'id': f'~account.tax.use~sale~account.tax~{self.tax_price_sale_10.id}~account.account~{self.inv_001.invoice_line_ids.account_id.id}',
                'name': self.inv_001.invoice_line_ids.account_id.display_name,
                'columns': {
                    'net': 150.0, 'tax': 15.0,
                },
            },
        ]
        self._check_report_value(lines, lines_expected_value)
