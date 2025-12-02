from datetime import datetime
from odoo.tests.common import tagged
from .common import AccountReportL10nVn


@tagged('post_install', '-at_install', 'post_install_l10n')
class CashFlow(AccountReportL10nVn):

    def setUp(self):
        super(CashFlow, self).setUp()
        self.AccountCashFlowReport = self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_report')

    def test_01_validate_cash_flow(self):
        # 01/08/2021    # 01a
        journal_items_01a = [{
            'account_id': self.default_account_1125.id,
            'debit': 55000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 50000,
            'tax_ids': [(6, 0, self.tax_price_vn_sale_10.ids)]
        },
        {
            'account_id': self.default_account_33311.id,
            'debit': 0,
            'credit': 5000,
            'tax_repartition_line_id': self.tax_repartition_line_vn_sale_10.id,
        }]
        journal_entry_01a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_01a)

        bank_stmt_items_01a = [{
            'account_id': self.default_account_1111.id,
            'debit': 55000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 55000
        }]
        bank_stmt_01a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_01a)
        (journal_entry_01a | bank_stmt_01a).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021    # 01b
        journal_items_01b_01 = [{
            'account_id': self.default_account_131.id,
            'debit': 45000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 40000,
        },
        {
            'account_id': self.default_account_3331.id,
            'debit': 0,
            'credit': 5000,
        }]
        journal_entry_01b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_01b_01)
        journal_items_01b_02 = [{
            'account_id': self.default_account_1125.id,
            'debit': 45000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 45000,
            'partner_id': self.customer_a.id,
        }]
        journal_entry_01b_02 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_01b_02)
        (journal_entry_01b_01 | journal_entry_01b_02).line_ids.filtered(lambda r: r.account_id.id == self.default_account_131.id and r.partner_id.id == self.customer_a.id).reconcile()

        bank_stmt_items_01b = [{
            'account_id': self.default_account_1111.id,
            'debit': 45000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 45000
        }]
        bank_stmt_01b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_01b)
        (journal_entry_01b_02 | bank_stmt_01b).line_ids.filtered(lambda r: r.account_id.id == self.default_account_1125.id).reconcile()

        # 01/08/2021 02a
        journal_items_02a = [{
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 66000,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 60000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 6000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        journal_entry_02a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_purchase, items=journal_items_02a)

        bank_stmt_items_02a = [{
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 66000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 66000,
            'credit': 0
        }]
        bank_stmt_02a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_02a)
        (journal_entry_02a | bank_stmt_02a).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 02b
        # Mua hàng
        journal_items_02b_1 = [{
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 44000,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 40000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 4000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        journal_entry_02b_1 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_purchase, items=journal_items_02b_1)
        # Trả NCC
        journal_items_02b_2 = [{
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 44000,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 44000,
            'credit': 0,
        }]
        journal_entry_02b_2 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_purchase, items=journal_items_02b_2)
        (journal_entry_02b_1 | journal_entry_02b_2).line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_02b = [{
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 44000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 44000,
            'credit': 0
        }]
        bank_stmt_02b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_02b)
        (journal_entry_02b_2 | bank_stmt_02b).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 03
        journal_items_03 = [{
            'account_id': self.default_account_3341.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_03 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_03)

        bank_stmt_items_03 = [{
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 500000,
            'credit': 0
        }]
        bank_stmt_03 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_03)
        (journal_entry_03 | bank_stmt_03).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 04
        journal_items_04 = [{
            'account_id': self.default_account_635.id,
            'debit': 10000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_borrowing_loan.ids)]
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_04 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_04)
        journal_items_04_01 = [{
            'account_id': self.default_account_331.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_04_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_04_01)
        (journal_entry_04 | journal_entry_04_01).line_ids.filtered(lambda r: r.account_id.id == self.default_account_331.id and r.partner_id.id == self.vendor_a.id).reconcile()

        bank_stmt_items_04 = [{
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 10000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 10000,
            'credit': 0
        }]
        bank_stmt_04 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_04)
        (journal_entry_04_01 | bank_stmt_04).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 05
        journal_items_05 = [{
            'account_id': self.default_account_3334.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 15000,
        }]
        journal_entry_05 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_05)

        bank_stmt_items_05 = [{
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 15000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 15000,
            'credit': 0
        }]
        bank_stmt_05 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_05)
        (journal_entry_05 | bank_stmt_05).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 21a
        journal_items_21a = [{
            'account_id': self.default_account_2112.id,
            'debit': 500000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_21a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_21a)

        bank_stmt_items_21a = [{
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 500000,
            'credit': 0
        }]
        bank_stmt_21a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_21a)
        (journal_entry_21a | bank_stmt_21a).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 21b
        journal_items_21b = [{
            'account_id': self.default_account_2112.id,
            'debit': 500000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 500000,
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_21b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_21b)
        journal_items_21b_01 = [{
            'account_id': self.default_account_331.id,
            'debit': 500000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_items_21b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_21b_01)
        (journal_entry_21b | journal_items_21b_01).line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_21b = [{
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 500000,
            'credit': 0
        }]
        bank_stmt_21b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_21b)
        (journal_items_21b_01 | bank_stmt_21b).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 22a
        journal_items_22a = [{
            'account_id': self.default_account_1125.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_711.id,
            'debit': 0,
            'credit': 50000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_liquidation_fixed_assets.ids)]
        }]
        journal_entry_22a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22a)

        bank_stmt_items_22a = [{
            'account_id': self.default_account_1111.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_22a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22a)
        (journal_entry_22a | bank_stmt_22a).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # # 01/08/2021 22b
        journal_items_22b = [{
            'account_id': self.default_account_131.id,
            'debit': 50000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_liquidation_fixed_assets.ids)],
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_711.id,
            'debit': 0,
            'credit': 50000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_liquidation_fixed_assets.ids)]
        }]
        journal_entry_22b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22b)
        journal_items_22b_01 = [{
            'account_id': self.default_account_1125.id,
            'debit': 50000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 50000,
            'partner_id': self.customer_a.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_liquidation_fixed_assets.ids)]
        }]
        journal_entry_22b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22b_01)
        (journal_entry_22b | journal_entry_22b_01).line_ids.filtered(lambda r: r.account_id.id == self.default_account_131.id and r.partner_id.id == self.customer_a.id).reconcile()

        bank_stmt_items_22b = [{
            'account_id': self.default_account_1111.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000,
            'partner_id': self.customer_a.id,
        }]
        bank_stmt_22b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22b)
        (journal_entry_22b_01 | bank_stmt_22b).line_ids.filtered(lambda r: r.account_id.id == self.default_account_1125.id).reconcile()

        # 01/08/2021    22c
        journal_items_22c = [{
            'account_id': self.default_account_811.id,
            'debit': 20000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_liquidation_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 20000,
        }]
        journal_entry_22c = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22c)

        bank_stmt_items_22c = [{
            'account_id': self.default_account_1126.id,
            'debit': 20000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 20000
        }]
        bank_stmt_22c = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22c)
        (journal_entry_22c | bank_stmt_22c).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021 22d
        journal_items_22d = [{
            'account_id': self.default_account_811.id,
            'debit': 20000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_liquidation_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 20000,
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_22d = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22d)
        journal_items_22d_01 = [{
            'account_id': self.default_account_331.id,
            'debit': 20000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 20000,
        }]
        journal_entry_22d_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22d_01)
        (journal_entry_22d | journal_entry_22d_01).line_ids.filtered(lambda r: r.account_id.code.startswith('331') and r.partner_id.id == self.vendor_a.id).reconcile()

        bank_stmt_items_22d = [{
            'account_id': self.default_account_1126.id,
            'debit': 20000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 20000
        }]
        bank_stmt_22d = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22d)
        (journal_entry_22d_01 | bank_stmt_22d).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021    23
        journal_items_23 = [{
            'account_id': self.default_account_1288.id,
            'debit': 50000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_lending_loan.ids)]
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 50000
        }]
        journal_entry_23 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_23)

        bank_stmt_items_23 = [{
            'account_id': self.default_account_1126.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_23 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_23)
        (journal_entry_23 | bank_stmt_23).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021    24
        journal_items_24 = [{
            'account_id': self.default_account_1125.id,
            'debit': 60000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1283.id,
            'debit': 0,
            'credit': 60000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_lending_loan.ids)]
        }]
        journal_entry_24 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_24)

        bank_stmt_items_24 = [{
            'account_id': self.default_account_1121.id,
            'debit': 60000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 60000
        }]
        bank_stmt_24 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_24)
        (journal_entry_24 | bank_stmt_24).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021    25a
        journal_items_25a = [{
            'account_id': self.default_account_221.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 700000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_lending_loan.ids)]
        }]
        journal_entry_25a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_25a)

        bank_stmt_items_25a = [{
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 700000
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 700000,
            'credit': 0
        }]
        bank_stmt_25a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_25a)
        (journal_entry_25a | bank_stmt_25a).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021    25b
        journal_items_25b = [{
            'account_id': self.default_account_221.id,
            'debit': 400000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 400000,
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_25b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_25b)
        journal_items_25b_01 = [{
            'account_id': self.default_account_331.id,
            'debit': 400000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 400000,
        }]
        journal_entry_25b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_25b_01)
        (journal_entry_25b | journal_entry_25b_01).line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_25b = [{
            'account_id': self.default_account_1126.id,
            'debit': 400000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 400000
        }]
        bank_stmt_25b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_25b)
        (journal_entry_25b_01 | bank_stmt_25b).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021
        journal_items_26a = [{
            'account_id': self.default_account_1125.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_221.id,
            'debit': 0,
            'credit': 700000,
        }]
        journal_entry_26a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_26a)

        bank_stmt_items_26a = [{
            'account_id': self.default_account_1121.id,
            'debit': 700000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 700000
        }]
        bank_stmt_26a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_26a)
        (journal_entry_26a | bank_stmt_26a).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021
        journal_items_26b = [{
            'account_id': self.default_account_131.id,
            'debit': 700000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_221.id,
            'debit': 0,
            'credit': 700000,
        }]
        journal_entry_26b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_26b)
        journal_items_26b_01 = [{
            'account_id': self.default_account_1125.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 700000,
            'partner_id': self.customer_a.id,
        }]
        journal_entry_26b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_26b_01)
        (journal_entry_26b | journal_entry_26b_01).line_ids.filtered(lambda r: r.account_id.id == self.default_account_131.id and r.partner_id.id == self.customer_a.id).reconcile()

        bank_stmt_items_26b = [{
            'account_id': self.default_account_1121.id,
            'debit': 700000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 700000
        }]
        bank_stmt_26b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_26b)
        (journal_entry_26b_01 | bank_stmt_26b).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021    27a
        journal_items_27a = [{
            'account_id': self.default_account_1125.id,
            'debit': 20000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_515.id,
            'debit': 0,
            'credit': 20000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_interests_dividends_distributed_profits.ids)]
        }]
        journal_entry_27a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_27a)

        bank_stmt_items_27a = [{
            'account_id': self.default_account_1121.id,
            'debit': 20000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 20000
        }]
        bank_stmt_27a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_27a)
        (journal_entry_27a | bank_stmt_27a).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021    27b
        journal_items_27b = [{
            'account_id': self.default_account_131.id,
            'debit': 30000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_515.id,
            'debit': 0,
            'credit': 30000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_interests_dividends_distributed_profits.ids)]
        }]
        journal_entry_27b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_27b)
        journal_items_27b_01 = [{
            'account_id': self.default_account_1125.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 30000,
            'partner_id': self.customer_a.id,
        }]
        journal_entry_27b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_27b_01)
        (journal_entry_27b | journal_entry_27b_01).line_ids.filtered(lambda r: r.account_id.id == self.default_account_131.id and r.partner_id.id == self.customer_a.id).reconcile()

        bank_stmt_items_27b = [{
            'account_id': self.default_account_1121.id,
            'debit': 30000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 30000
        }]
        bank_stmt_27b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_27b)
        (journal_entry_27b_01 | bank_stmt_27b).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021    31
        journal_items_31 = [{
            'account_id': self.default_account_1125.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4111.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_31 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_31)

        bank_stmt_items_31 = [{
            'account_id': self.default_account_1121.id,
            'debit': 500000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 500000
        }]
        bank_stmt_31 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_31)
        (journal_entry_31 | bank_stmt_31).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021    32
        journal_items_32 = [{
            'account_id': self.default_account_4111.id,
            'debit': 200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 200000,
        }]
        journal_entry_32 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_32)

        bank_stmt_items_32 = [{
            'account_id': self.default_account_1126.id,
            'debit': 200000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 200000
        }]
        bank_stmt_32 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_32)
        (journal_entry_32 | bank_stmt_32).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021    33
        journal_items_33 = [{
            'account_id': self.default_account_1125.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3411.id,
            'debit': 0,
            'credit': 100000,
        }]
        journal_entry_33 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_33)

        bank_stmt_items_33 = [{
            'account_id': self.default_account_1121.id,
            'debit': 100000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 100000
        }]
        bank_stmt_33 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_33)
        (journal_entry_33 | bank_stmt_33).line_ids.filtered(lambda r: r.account_id.code == '1125').reconcile()

        # 01/08/2021
        journal_items_34 = [{
            'account_id': self.default_account_3411.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 100000,
        }]
        journal_entry_34 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_34)
        (journal_entry_33 | journal_entry_34).line_ids.filtered(lambda r: r.account_id.code == '3411').reconcile()

        bank_stmt_items_34 = [{
            'account_id': self.default_account_1126.id,
            'debit': 100000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 100000
        }]
        bank_stmt_34 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_34)
        (journal_entry_34 | bank_stmt_34).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021    35
        journal_items_35 = [{
            'account_id': self.default_account_3412.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_35 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_35)

        bank_stmt_items_35 = [{
            'account_id': self.default_account_1126.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_35 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_35)
        (journal_entry_35 | bank_stmt_35).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021
        journal_items_36a = [{
            'account_id': self.default_account_4212.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_36a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_36a)

        bank_stmt_items_36a = [{
            'account_id': self.default_account_1126.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_36a = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_36a)
        (journal_entry_36a | bank_stmt_36a).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 01/08/2021
        journal_items_36b = [{
            'account_id': self.default_account_4212.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3388.id,
            'debit': 0,
            'credit': 50000,
            'partner_id': self.vendor_b.id,
        }]
        journal_entry_36b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_36b)
        journal_items_36b_01 = [{
            'account_id': self.default_account_3388.id,
            'debit': 50000,
            'credit': 0,
            'partner_id': self.vendor_b.id,
        },
        {
            'account_id': self.default_account_1126.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_36b_01 = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_36b_01)
        (journal_entry_36b | journal_entry_36b_01).line_ids.filtered(lambda r: r.account_id.code.startswith('3388')).reconcile()

        bank_stmt_items_36b = [{
            'account_id': self.default_account_1126.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_36b = self._init_journal_entry(None, datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_36b)
        (journal_entry_36b_01 | bank_stmt_36b).line_ids.filtered(lambda r: r.account_id.code == '1126').reconcile()

        # 09/08/2020
        journal_items_60 = [{
            'account_id': self.default_account_1121.id,
            'debit': 150000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4111.id,
            'debit': 0,
            'credit': 150000,
        }]
        self._init_journal_entry(None, datetime(2020, 8, 9, 12, 0), self.default_journal_vn_misc, items=journal_items_60)
        lines_to_check = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 12, 31, 0, 0), filter_option='custom', date_from=datetime(2021, 1, 1, 0, 0), date_to=datetime(2021, 12, 31, 0, 0), cash_basis=False)
        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01').id,
                'name': 'I. Cash flow from operating activities',
                'columns': {'balance': -535000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_01').id,
                'name': '1. Receipts from sales of goods and provision of services',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_01_01').id,
                'name': '1.1 Direct cash payments',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_01_02').id,
                'name': '1.2 Receivables',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_02').id,
                'name': '2. Payments to suppliers of goods and services',
                'columns': {'balance': -66000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_02_01').id,
                'name': '2.1 Direct cash payments',
                'columns': {'balance': -66000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_02_02').id,
                'name': '2.2. Payable',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_03').id,
                'name': '3. Payments to employees',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_04').id,
                'name': '4. Paid interest',
                'columns': {'balance': -10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_04_01').id,
                'name': '4.1 Direct cash payments',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_04_02').id,
                'name': '4.2 Payable',
                'columns': {'balance': -10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_05').id,
                'name': '5. Company income tax paid',
                'columns': {'balance': -15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_06').id,
                'name': '6. Other receipts from operating activities',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_01_07').id,
                'name': '7. Other payments for operating activities',
                'columns': {'balance': -544000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02').id,
                'name': 'II. Cash flows from investing activities',
                'columns': {'balance': -580000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_01').id,
                'name': '1. Payments for additions to fixed assets and other long-term assets',
                'columns': {'balance': -1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_01_01').id,
                'name': '1.1 Direct cash payments',
                'columns': {'balance': -500000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_01_02').id,
                'name': '1.2 Payable',
                'columns': {'balance': -500000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_02').id,
                'name': '2. Collections on disposals of fixed assets and other long-term assets',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_02_01').id,
                'name': '2.1 Revenue of fixed assets and other long-term assets (Cash Direct)',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_02_02').id,
                'name': '2.2 Expenses of fixed assets and other long-term assets (Cash Direct)',
                'columns': {'balance': -20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_02_03').id,
                'name': '2.3 Revenue of fixed assets and other long-term assets (Via Receivables)',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_02_04').id,
                'name': '2.4 Expenses of fixed assets and other long-term assets (Via Payables)',
                'columns': {'balance': -20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_03').id,
                'name': '3. Granting loans, buying debt instruments of other entities',
                'columns': {'balance': -50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_04').id,
                'name': '4. Recovery of loan given and disposals of debt instruments of other entities',
                'columns': {'balance': 60000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_05').id,
                'name': '5. Investments in equity of other entities',
                'columns': {'balance': -1100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_05_01').id,
                'name': '5.1 Direct cash payments',
                'columns': {'balance': -700000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_05_02').id,
                'name': '5.2 Payable',
                'columns': {'balance': -400000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_06').id,
                'name': '6. Withdrawals of investments in other entities',
                'columns': {'balance': 1400000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_06_01').id,
                'name': '6.1 Direct cash payments',
                'columns': {'balance': 700000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_06_02').id,
                'name': '6.2 Payable',
                'columns': {'balance': 700000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_07').id,
                'name': '7. Interests, dividends and profits distributed',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_07_01').id,
                'name': '7.1 Direct cash payments',
                'columns': {'balance': 20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_02_07_02').id,
                'name': '7.2 Payable',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03').id,
                'name': 'III. Cash flows from financing activities',
                'columns': {'balance': 250000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_01').id,
                'name': '1. Collection on share issuance and capital contributions from shareholders',
                'columns': {'balance': 500000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_02').id,
                'name': '2. Returning Owner\'s capital in cash and Purchasing Treasury Stocks',
                'columns': {'balance': -200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_03').id,
                'name': '3. Receipts from borrowings',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_04').id,
                'name': '4. Payments to settle loan principals',
                'columns': {'balance': -100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_05').id,
                'name': '5. Payments to settle financial lease principals',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_06').id,
                'name': '6. Dividends, profits distributed',
                'columns': {'balance': -50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_06_01').id,
                'name': '6.1 Direct cash payments',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_03_06_02').id,
                'name': '6.2 Payable',
                'columns': {'balance': -50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_04').id,
                'name': 'Net cash flows during the year (50 = 20 + 30 + 40)',
                'columns': {'balance': -865000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_05').id,
                'name': 'Cash and cash equivalent at the beginning of the year',
                'columns': {'balance': 150000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_06').id,
                'name': 'Currency translation differences',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.cash_flow_c200_line_07').id,
                'name': 'Cash and cash equivalent at the end of the year (70 = 50 + 60 + 61)',
                'columns': {'balance': -715000.0, }
            }
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
