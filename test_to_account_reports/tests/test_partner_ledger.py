from datetime import datetime, date

from odoo.tests.common import tagged
from odoo.tools.misc import format_date

from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class PartnerLedger(AccountReportsCommon):

    def setUp(self):
        super(PartnerLedger, self).setUp()
        self.AccountPartnerLedger = self.env.ref('to_account_reports.partner_ledger_report')

    def test_01_validate_partner_ledger(self):
        # 11/08/2021 Create vendor bill 10 for vendor a
        bill_date = date(2021, 8, 11)        # 11/08/2021
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            bill_001 = self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[10], taxes=[])

        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Vendor A        |              |              |           |                |                 |           |       10   |       -10  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Total           |              |              |           |                |                 |           |       10   |       -10  |
        # """
        lines_to_check = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 11, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~res.partner~{self.vendor_a.id}',
                'name': 'Vendor A',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 0, 'credit': 10, 'balance': -10},
            }, {
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 0, 'credit': 10, 'balance': -10},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 12/08/2021 Create vendor bill 5 for vendor a
        bill_date = date(2021, 8, 12)        # 12/08/2021
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            bill_002 = self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[5], taxes=[])
        aml_payable_002 = bill_002.line_ids.filtered(lambda l: l.account_id.account_type == 'liability_payable')
        # """
        # |------------|
        # |Expect value line Vendor A|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Initial Balance |              |              |           |                |                 |           |       10   |       -10  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # 2021-08-12      |              |              |           |                |                 |           |        5   |       -15  |
        # """
        report_lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 12, 12, 0), 'custom', date(2021, 8, 12), date(2021, 12, 31))
        line_to_check = self._get_expanded_lines_report(self.AccountPartnerLedger, report_lines[0], datetime(2021, 8, 12, 12, 0), 'custom', date(2021, 8, 12), date(2021, 12, 31))
        lines_expected_value = [{
                'id': f'~res.partner~{self.vendor_a.id}|initial-balance',
                'name': 'Initial Balance',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 0, 'credit': 10, 'balance': -10},
            }, {
                'id': f'~res.partner~{self.vendor_a.id}|~account.move.line~{aml_payable_002.id}',
                'name': aml_payable_002.date,
                'columns': {
                    'journal_code': bill_002.journal_id.code,
                    'account_code': aml_payable_002.account_id.code,
                    'ref': bill_002.name,
                    'date_maturity': format_date(self.env, aml_payable_002.date_maturity),
                    'matching_number': '',
                    'debit': 0,
                    'credit': 5,
                    'balance': -15
                },
            }
        ]
        self._check_report_value(line_to_check, lines_expected_value)

        # 13/08/2021 Create vendor payment 5 for vendor a
        bill_002_payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=bill_002.ids).create({
            'payment_date': date(2021, 8, 13),
            'journal_id': self.default_journal_bank.id,
            'amount': 5,
        })._create_payments()
        _liquidity_lines, counterpart_lines, _writeoff_lines = bill_002_payment._seek_for_lines()
        # """
        # |------------|
        # |Expect value line Vendor A|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Initial Balance |              |              |           |                |                 |           |       15   |       -15  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # 2021-08-13      |              |              |           |                |                 |       5   |        0   |       -10  |
        # """
        report_lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 8, 13), date(2021, 12, 31))
        line_to_check = self._get_expanded_lines_report(self.AccountPartnerLedger, report_lines[0], datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 8, 13), date(2021, 12, 31))
        lines_expected_value = [{
                'id': f'~res.partner~{self.vendor_a.id}|initial-balance',
                'name': 'Initial Balance',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 0, 'credit': 15, 'balance': -15},
            }, {
                'id': f'~res.partner~{self.vendor_a.id}|~account.move.line~{counterpart_lines[0].id}',
                'name': bill_002_payment.date,
                'columns': {
                    'journal_code': bill_002_payment.journal_id.code,
                    'account_code': counterpart_lines[0].account_id.code,
                    'ref': bill_002_payment.name,
                    'date_maturity': format_date(self.env, bill_002_payment.date),
                    'matching_number': counterpart_lines[0].matching_number,
                    'debit': 5,
                    'credit': 0,
                    'balance': -10,
                },
            }
        ]
        self._check_report_value(line_to_check, lines_expected_value)

        # 14/08/2021 Create vendor payment 10 for vendor a
        bill_001_payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=bill_001.ids).create({
            'payment_date': date(2021, 8, 14),
            'journal_id': self.default_journal_bank.id,
            'amount': 10,
        })._create_payments()
        _liquidity_lines, counterpart_lines, _writeoff_lines = bill_001_payment._seek_for_lines()
        # """
        # |------------|
        # |Expect value line Vendor A|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Initial Balance |              |              |           |                |                 |      5    |       15   |       -10  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # 2021-08-14      |              |              |           |                |                 |      10   |        0   |         0  |
        # """
        report_lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 14, 12, 0), 'custom', date(2021, 8, 14), date(2021, 12, 31))
        line_to_check = self._get_expanded_lines_report(self.AccountPartnerLedger, report_lines[0], datetime(2021, 8, 14, 12, 0), 'custom', date(2021, 8, 14), date(2021, 12, 31))
        lines_expected_value = [{
                'id': f'~res.partner~{self.vendor_a.id}|initial-balance',
                'name': 'Initial Balance',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 5, 'credit': 15, 'balance': -10},
            }, {
                'id': f'~res.partner~{self.vendor_a.id}|~account.move.line~{counterpart_lines[0].id}',
                'name': bill_001_payment.date,
                'columns': {
                    'journal_code': bill_001_payment.journal_id.code,
                    'account_code': counterpart_lines[0].account_id.code,
                    'ref': bill_001_payment.name,
                    'date_maturity': format_date(self.env, bill_001_payment.date),
                    'matching_number': counterpart_lines[0].matching_number,
                    'debit': 10,
                    'credit': 0,
                    'balance': 0,
                },
            }
        ]
        self._check_report_value(line_to_check, lines_expected_value)

    def test_02_validate_partner_ledger(self):
        # 11/08/2021 Create customer invoice 10 for customer a
        inv_date = date(2021, 8, 11)        # 11/08/2021
        with self.patch_datetime_now(inv_date), self.patch_date_today(inv_date), self.patch_date_context_today(inv_date):
            invoice_001 = self.init_invoice("out_invoice", self.customer_a, inv_date, post=True, amounts=[10], taxes=[])
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Customer A      |              |              |           |                |                 |      10   |            |        10  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Total           |              |              |           |                |                 |      10   |            |        10  |
        # """
        lines_to_check = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 11, 12, 0), 'this_year')
        lines_expected_value = [{
                'id': f'~res.partner~{self.customer_a.id}',
                'name': 'Customer A',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 10, 'credit': 0, 'balance': 10},
            }, {
                'id': '~res.partner~total',
                'name': 'Total',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 10, 'credit': 0, 'balance': 10},
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 12/08/2021 Create customer invoice 5 for customer a
        inv_date = date(2021, 8, 12)        # 12/08/2021
        with self.patch_datetime_now(inv_date), self.patch_date_today(inv_date), self.patch_date_context_today(inv_date):
            invoice_002 = self.init_invoice("out_invoice", self.customer_a, inv_date, post=True, amounts=[5], taxes=[])
        aml_receivable_002 = invoice_002.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable')
        # """
        # |------------|
        # |Expect value line Customer A|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Initial Balance |              |              |           |                |                 |      10   |            |       10  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # 2021-08-12      |              |              |           |                |                 |       5   |            |       15  |
        # """
        report_lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 12, 12, 0), 'custom', date(2021, 8, 12), date(2021, 12, 31))
        line_to_check = self._get_expanded_lines_report(self.AccountPartnerLedger, report_lines[0], datetime(2021, 8, 12, 12, 0), 'custom', date(2021, 8, 12), date(2021, 12, 31))
        lines_expected_value = [{
                'id': f'~res.partner~{self.customer_a.id}|initial-balance',
                'name': 'Initial Balance',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 10, 'credit': 0, 'balance': 10},
            }, {
                'id': f'~res.partner~{self.customer_a.id}|~account.move.line~{aml_receivable_002.id}',
                'name': aml_receivable_002.date,
                'columns': {
                    'journal_code': invoice_002.journal_id.code,
                    'account_code': aml_receivable_002.account_id.code,
                    'ref': invoice_002.name,
                    'date_maturity': format_date(self.env, aml_receivable_002.date_maturity),
                    'matching_number': '',
                    'debit': 5,
                    'credit': 0,
                    'balance': 15,
                },
            }
        ]
        self._check_report_value(line_to_check, lines_expected_value)

        # 13/08/2021 Create customer payment 5 for customer a
        invoice_002_payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice_002.ids).create({
            'payment_date': date(2021, 8, 13),
            'journal_id': self.default_journal_bank.id,
            'amount': 5,
        })._create_payments()
        _liquidity_lines, counterpart_lines, _writeoff_lines = invoice_002_payment._seek_for_lines()
        # """
        # |------------|
        # |Expect value line Customer A|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Initial Balance |              |              |           |                |                 |      15   |            |       15   |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # 2021-08-13      |              |              |           |                |                 |           |        5   |       10   |
        # """
        report_lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 8, 13), date(2021, 12, 31))
        line_to_check = self._get_expanded_lines_report(self.AccountPartnerLedger, report_lines[0], datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 8, 13), date(2021, 12, 31))
        lines_expected_value = [{
                'id': f'~res.partner~{self.customer_a.id}|initial-balance',
                'name': 'Initial Balance',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 15, 'credit': 0, 'balance': 15},
            }, {
                'id': f'~res.partner~{self.customer_a.id}|~account.move.line~{counterpart_lines[0].id}',
                'name': counterpart_lines.date,
                'columns': {
                    'journal_code': invoice_002_payment.journal_id.code,
                    'account_code': counterpart_lines.account_id.code,
                    'ref': invoice_002_payment.name,
                    'date_maturity': format_date(self.env, counterpart_lines[0].date_maturity),
                    'matching_number': counterpart_lines[0].matching_number,
                    'debit': 0.0,
                    'credit': 5.0,
                    'balance': 10.0,
                },
            }
        ]
        self._check_report_value(line_to_check, lines_expected_value)

        # 14/08/2021 Create customer payment 10 for customer a
        invoice_001_payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice_001.ids).create({
            'payment_date': date(2021, 8, 14),
            'journal_id': self.default_journal_bank.id,
            'amount': 10,
        })._create_payments()
        _liquidity_lines, counterpart_lines, _writeoff_lines = invoice_001_payment._seek_for_lines()
        # """
        # |------------|
        # |Expect value line Customer A|
        # |------------|
        #
        #                 | journal_code | account_code |    ref    | date_maturity  | matching_number |   debit   |   credit   |   balance  |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # Initial Balance |              |              |           |                |                 |      15   |        5   |       10   |
        # ----------------|--------------|--------------|-----------|----------------|-----------------|-----------|------------|------------|
        # 2021-08-14      |              |              |           |                |                 |           |       10   |            |
        # """
        report_lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 14, 12, 0), 'custom', date(2021, 8, 14), date(2021, 12, 31))
        line_to_check = self._get_expanded_lines_report(self.AccountPartnerLedger, report_lines[0], datetime(2021, 8, 14, 12, 0), 'custom', date(2021, 8, 14), date(2021, 12, 31))
        lines_expected_value = [{
                'id': f'~res.partner~{self.customer_a.id}|initial-balance',
                'name': 'Initial Balance',
                'columns': {'journal_code': '', 'account_code': '', 'ref': '', 'date_maturity': '', 'matching_number': '', 'debit': 15.0, 'credit': 5.0, 'balance': 10.0},
            }, {
                'id': f'~res.partner~{self.customer_a.id}|~account.move.line~{counterpart_lines[0].id}',
                'name': counterpart_lines.date,
                'columns': {
                    'journal_code': invoice_001_payment.journal_id.code,
                    'account_code': counterpart_lines.account_id.code,
                    'ref': invoice_001_payment.name,
                    'date_maturity': format_date(self.env, counterpart_lines[0].date_maturity),
                    'matching_number': counterpart_lines[0].matching_number,
                    'debit': 0.0,
                    'credit': 10.0,
                    'balance': 0.0,
                },
            }
        ]
        self._check_report_value(line_to_check, lines_expected_value)
