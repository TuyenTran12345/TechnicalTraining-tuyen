from datetime import datetime, date
from odoo.tests.common import tagged, Form
from .common import AccountReportsCommon


@tagged('post_install', '-at_install')
class GeneralLedger(AccountReportsCommon):

    def setUp(self):
        super(GeneralLedger, self).setUp()
        self.AccountGeneralLedger = self.env.ref('to_account_reports.general_ledger_report')

    def test_01_validate_general_ledger(self):
        # 13/08/2021 Create vendor bill 10 for vendor a
        bill_date = date(2021, 8, 13)
        with self.patch_datetime_now(bill_date), self.patch_date_today(bill_date), self.patch_date_context_today(bill_date):
            bill = self.init_invoice("in_invoice", self.vendor_a, bill_date, post=True, amounts=[10], taxes=[])
        aml_payable = bill.line_ids.filtered(lambda line: line.account_id.account_type == 'liability_payable')
        aml_expense = bill.line_ids - aml_payable
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 211000 Account Payable    |              |                |                |                 |                |        10      |         -10    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 600000 Expenses           |              |                |                |                 |         10     |                |          10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{aml_payable.account_id.id}',
                'name': aml_payable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 10.0,
                    'balance': -10,
                },
            },
            {
                'id': f'~account.account~{aml_expense.account_id.id}',
                'name': aml_expense.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 0.0,
                    'balance': 10.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 13/08/2021 Create vendor payment 10 for vendor a
        payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=bill.ids).create({
            'payment_date': date(2021, 8, 13),
            'journal_id': self.default_journal_bank.id,
            'amount': 10,
        })._create_payments()
        liquidity_lines, counterpart_lines, _writeoff_lines = payment._seek_for_lines()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 101403 Outstanding        |              |                |                |                 |                |         10     |         -10    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 211000 Account Payable    |              |                |                |                 |         10     |        10      |                |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 600000 Expenses           |              |                |                |                 |         10     |                |         -10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{liquidity_lines.account_id.id}',
                'name': liquidity_lines.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 10.0,
                    'balance': -10.0,
                },
            },
            {
                'id': f'~account.account~{aml_payable.account_id.id}',
                'name': aml_payable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 10.0,
                    'balance': 0.0,
                },
            },
            {
                'id': f'~account.account~{aml_expense.account_id.id}',
                'name': aml_expense.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 0.0,
                    'balance': 10.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # Change the value of journal entry 1 from 10 to 15
        bill.button_draft()
        with Form(bill) as bill_form:
            with bill_form.invoice_line_ids.edit(0) as line_form:
                line_form.price_unit = 15
        bill.action_post()
        (aml_payable + counterpart_lines).reconcile()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 101403 Outstanding        |              |                |                |                 |                |         10     |         -10    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 211000 Account Payable    |              |                |                |                 |         10     |        15      |          -5    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 600000 Expenses           |              |                |                |                 |         15     |                |          15    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{liquidity_lines.account_id.id}',
                'name': liquidity_lines.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 10.0,
                    'balance': -10.0,
                },
            },
            {
                'id': f'~account.account~{aml_payable.account_id.id}',
                'name': aml_payable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 15.0,
                    'balance': -5.0,
                },
            },
            {
                'id': f'~account.account~{aml_expense.account_id.id}',
                'name': aml_expense.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 15.0,
                    'credit': 0.0,
                    'balance': 15.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # Change the value of journal entry 2 from 10 to 15
        payment.action_draft()
        with Form(payment) as payment_form:
            payment_form.amount = 15
        payment.action_post()
        (aml_payable + counterpart_lines).reconcile()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 101403 Outstanding        |              |                |                |                 |                |         15     |         -15    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 211000 Account Payable    |              |                |                |                 |         15     |        15      |           0    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 600000 Expenses           |              |                |                |                 |         15     |                |          15    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{liquidity_lines.account_id.id}',
                'name': liquidity_lines.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 15.0,
                    'balance': -15.0,
                },
            },
            {
                'id': f'~account.account~{aml_payable.account_id.id}',
                'name': aml_payable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 15.0,
                    'credit': 15.0,
                    'balance': 0.0,
                },
            },
            {
                'id': f'~account.account~{aml_expense.account_id.id}',
                'name': aml_expense.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 15.0,
                    'credit': 0.0,
                    'balance': 15.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

    def test_02_validate_general_ledger(self):
        # 13/08/2021 Create vendor bill 10 for vendor a
        inv_date = date(2021, 8, 13)
        with self.patch_datetime_now(inv_date), self.patch_date_today(inv_date), self.patch_date_context_today(inv_date):
            invoice = self.init_invoice("out_invoice", self.customer_a, inv_date, post=True, amounts=[10], taxes=[])
        aml_receivable = invoice.line_ids.filtered(lambda line: line.account_id.account_type == 'asset_receivable')
        aml_product = invoice.line_ids - aml_receivable
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 121000 Account Receivable |              |                |                |                 |         10     |                |          10    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 400000 Product Sales      |              |                |                |                 |                |         10     |         -10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{aml_receivable.account_id.id}',
                'name': aml_receivable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 0.0,
                    'balance': 10.0,
                },
            },
            {
                'id': f'~account.account~{aml_product.account_id.id}',
                'name': aml_product.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 10.0,
                    'balance': -10.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # 13/08/2021 Create vendor payment 10 for vendor a
        payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'payment_date': date(2021, 8, 13),
            'journal_id': self.default_journal_bank.id,
            'amount': 10,
        })._create_payments()
        liquidity_lines, counterpart_lines, _writeoff_lines = payment._seek_for_lines()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 101403 Outstanding        |              |                |                |                 |         10     |                |          10    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 121000 Account Receivable |              |                |                |                 |         10     |          10    |                |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 400000 Product Sales      |              |                |                |                 |                |          10     |         -10    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{liquidity_lines.account_id.id}',
                'name': liquidity_lines.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 0.0,
                    'balance': 10.0,
                },
            },
            {
                'id': f'~account.account~{aml_receivable.account_id.id}',
                'name': aml_receivable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 10.0,
                    'balance': 0.0,
                },
            },
            {
                'id': f'~account.account~{aml_product.account_id.id}',
                'name': aml_product.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 10.0,
                    'balance': -10.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # Change the price of journal entry 1 from 10 to 15
        invoice.button_draft()
        with Form(invoice) as bill_form:
            with bill_form.invoice_line_ids.edit(0) as line_form:
                line_form.price_unit = 15
        invoice.action_post()
        (aml_receivable + counterpart_lines).reconcile()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 101403 Outstanding        |              |                |                |                 |         10     |                |          10    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 121000 Account Receivable |              |                |                |                 |         15     |          10    |           5    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 400000 Product Sales      |              |                |                |                 |                |          15    |         -15    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{liquidity_lines.account_id.id}',
                'name': liquidity_lines.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 10.0,
                    'credit': 0.0,
                    'balance': 10.0,
                },
            },
            {
                'id': f'~account.account~{aml_receivable.account_id.id}',
                'name': aml_receivable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 15.0,
                    'credit': 10.0,
                    'balance': 5.0,
                },
            },
            {
                'id': f'~account.account~{aml_product.account_id.id}',
                'name': aml_product.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 15.0,
                    'balance': -15.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)

        # Change the price of journal entry 2 from 10 to 15
        payment.action_draft()
        with Form(payment) as payment_form:
            payment_form.amount = 15
        payment.action_post()
        (aml_receivable + counterpart_lines).reconcile()
        # """
        # |------------|
        # |Expect value|
        # |------------|
        #
        #                           |     date     | communication  |  partner_name  | amount_currency |      debit     |     credit     |     balance    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 101403 Outstanding        |              |                |                |                 |         15     |                |          15    |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 121000 Account Receivable |              |                |                |                 |         15     |          15    |                |
        # --------------------------|--------------|----------------|----------------|-----------------|----------------|----------------|----------------|
        # 400000 Product Sales      |              |                |                |                 |                |          15     |         -15    |
        # """
        lines_to_check = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        lines_expected_value = [{
                'id': f'~account.account~{liquidity_lines.account_id.id}',
                'name': liquidity_lines.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 15.0,
                    'credit': 0.0,
                    'balance': 15.0,
                },
            },
            {
                'id': f'~account.account~{aml_receivable.account_id.id}',
                'name': aml_receivable.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 15.0,
                    'credit': 15.0,
                    'balance': 0.0,
                },
            },
            {
                'id': f'~account.account~{aml_product.account_id.id}',
                'name': aml_product.account_id.display_name,
                'columns': {
                    'date': '',
                    'communication': '',
                    'partner_name': '',
                    'amount_currency': '',
                    'debit': 0.0,
                    'credit': 15.0,
                    'balance': -15.0,
                },
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
