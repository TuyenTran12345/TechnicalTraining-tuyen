from datetime import datetime, date
from odoo.tests.common import tagged
from .common import AccountReportL10nVn


@tagged('post_install', '-at_install', 'post_install_l10n')
class BalanceSheet(AccountReportL10nVn):

    def setUp(self):
        super(BalanceSheet, self).setUp()
        self.AccountBalanceSheetReport = self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_report')

    def _check_balance_sheet(self, lines_to_check, line_total_asset_id, line_total_equity_id):
        asset = equity = 0.0
        for line in lines_to_check:
            if line['id'] == line_total_asset_id:
                asset = line['columns']['balance']['value']
            if line['id'] == line_total_equity_id:
                equity = line['columns']['balance']['value']
        self.assertTrue(asset > 0 and equity > 0)
        self.assertEqual(asset, equity)

    def test_01_validate_balance_sheet(self):
        """
        |------------|
        |Expect value|
        |------------|
        Line items                                                                  | Code | Note | As of time |
        ----------------------------------------------------------------------------|------|------|------------|
        Total A - CURRENT ASSETS                                                    | 100  |      |            |
        (100 = 110 + 120 + 130 + 140 + 150)                                         |      |      |            |
            Total I. Cash and Cash Equivalents                                      | 110  |      |            |
            (110 = 111 + 112)                                                       |      |      |            |
                1. Bank & Cash                                                      | 111  |      |            |
                2. Cash equivalents                                                 | 112  |      |            |
            Total II. Short-term financial investments                              | 120  |      |            |
            (120 = 121 + 122 + 123)                                                 |      |      |            |
                1. Trading securities                                               | 121  |      |            |
                2. Allowances for decline in value of trading securities            | 122  |      |            |
                3. Held to maturity investments                                     | 123  |      |            |
            Total III. Short-term receivables                                       | 130  |      |            |
            (130 = 131 + 132 + 133 + 134 + 135 + 136 + 137 + 139)                   |      |      |            |
                1. Short-term trade receivables                                     | 131  |      |            |
                2. Short-term prepayments to suppliers                              | 132  |      |            |
                3. Short-term intra-company receivables                             | 133  |      |            |
                4. Receivables under schedule of construction contract              | 134  |      |            |
                5. Short-term loan receivables                                      | 135  |      |            |
                6. Other short-term receivables                                     | 136  |      |            |
                7. Short-term allowances for doubtful debts                         | 137  |      |            |
                8. Shortage of assets awaiting resolution                           | 139  |      |            |
            Total IV. Inventories (140 = 141 + 149)                                 | 140  |      |            |
                Total 1. Inventories                                                | 141  |      |            |
                    1.a. All Inventories                                            | 141a |      |            |
                    1.b. Minus Long-term work in progress                           | 141b |      |            |
                    1.c. Minus Long-term equipment and spare parts for replacement  | 141c |      |            |
                2. Allowances for decline in value of inventories                   | 149  |      |            |
            Total V. Other current assets (150 = 151 + 152 + 153 + 154 + 155)       | 150  |      |            |
                1. Short-term prepaid expenses                                      | 151  |      |            |
                2. Deductible VAT                                                   | 152  |      |            |
                3. Taxes and other receivables from government budget               | 153  |      |            |
                4. Government bonds purchased for resale                            | 154  |      |            |
                5. Other current assets                                             | 155  |      |            |
        Total B - NON-CURRENT ASSETS (200 = 210 + 220 + 240 + 250 + 260)            | 200  |      |            |
            Total I. Long-term receivables                                          | 210  |      |            |
            (210 = 211 + 212 + 213 + 214 + 215 + 216 + 219)                         |      |      |            |
                1. Long-term trade receivables                                      | 211  |      |            |
                2. Long-term prepayments to suppliers                               | 212  |      |            |
                3. Working capital provided to sub-units                            | 213  |      |            |
                4. Long-term intra-company receivables                              | 214  |      |            |
                5. Long-term loan receivables                                       | 215  |      |            |
                Total 6. Other long-term receivables                                | 216  |      |            |
                    6a. Other long-term receivables (assets)                        |      |      |            |
                    6b. Other long-term receivables (equity)                        |      |      |            |
                7. Long-term allowances for doubtful debts                          | 219  |      |            |
            Total II. Fixed assets (220 = 221 + 224 + 227 + 230)                    | 220  |      |            |
                Total 1. Tangible fixed assets (221 = 222 + 223)                    | 221  |      |            |
                    - Historical costs                                              | 222  |      |            |
                    - Accumulated depreciation                                      | 223  |      |            |
                Total 2. Finance lease fixed assets (224 = 225 + 226)               | 224  |      |            |
                    - Historical costs                                              | 225  |      |            |
                    - Accumulated depreciation                                      | 226  |      |            |
                Total 3. Intangible fixed assets (227 = 228 + 229)                  | 227  |      |            |
                    - Historical costs                                              | 228  |      |            |
                    - Accumulated depreciation                                      | 229  |      |            |
            Total III. Investment properties (230 = 231 + 232)                      | 230  |      |            |
                - Historical costs                                                  | 231  |      |            |
                - Accumulated depreciation                                          | 232  |      |            |
            Total IV. Long-term assets in progress (240 = 241 + 242)                | 240  |      |            |
                1. Long-term work in progress                                       | 241  |      |            |
                2. Construction in progress                                         | 242  |      |            |
            Total V. Long-term investments (250 = 251 + 252 + 253 + 254 + 255)      | 250  |      |            |
                1. Investments in subsidiaries                                      | 251  |      |            |
                2. Investments in joint ventures and associates                     | 252  |      |            |
                3. Investments in equity of other entities                          | 253  |      |            |
                4. Allowances for long-term investments                             | 254  |      |            |
                5. Held to maturity investments                                     | 255  |      |            |
            Total VI. Other long-term assets (260 = 261 + 262 + 263 + 268)          | 260  |      |            |
                1. Long-term prepaid expenses                                       | 261  |      |            |
                2. Deferred income tax assets                                       | 262  |      |            |
                3. Long-term equipment and spare parts for replacement              | 263  |      |            |
                4. Other long-term assets                                           | 268  |      |            |
        TOTAL ASSETS (270 = 100 + 200)                                              | 270  |      |            |
        Total C - LIABILITIES (300 = 310 + 330)                                     | 300  |      |            |
            Total I. Short-term liabilities                                         | 310  |      |            |
            (310 = 311 + 312 + 313 + 314 + 315                                      |      |      |            |
             + 316 + 317 + 318 + 319 + 320 + 321 + 322 + 323 + 324)                 |      |      |            |
                1. Short-term trade payables                                        | 311  |      |            |
                2. Short-term prepayments from customers                            | 312  |      |            |
                3. Taxes and other payables to government budget                    | 313  |      |            |
                4. Payables to employees                                            | 314  |      |            |
                5. Short-term accrued expenses                                      | 315  |      |            |
                6. Short-term intra-company payables                                | 316  |      |            |
                7. Payables under schedule of construction contract                 | 317  |      |            |
                8. Short-term unearned revenues                                     | 318  |      |            |
                9. Other short-term payments                                        | 319  |      |            |
                10. Short-term borrowings and finance lease liabilities             | 320  |      |            |
                11. Short-term provisions                                           | 321  |      |            |
                12. Bonus and welfare fund                                          | 322  |      |            |
                13. Price stabilization fund                                        | 323  |      |            |
                14. Government bonds purchased for resale                           | 324  |      |            |
            Total II. Long-term liabilities                                         | 330  |      |            |
            (330 = 331 + 332 + 333 + 334 + 335 + 336 + 337                          |      |      |            |
             + 338 + 339 + 340 + 341 + 342 + 343)                                   |      |      |            |
                1. Long-term trade payables                                         | 331  |      |            |
                2. Long-term prepayments from customers                             | 332  |      |            |
                3. Long-term accrued expenses                                       | 333  |      |            |
                4. Intra-company payables for operating capital received            | 334  |      |            |
                5. Long-term intra-company payables                                 | 335  |      |            |
                6. Long-term unearned revenues                                      | 336  |      |            |
                7. Other long-term payables                                         | 337  |      |            |
                8. Long-term borrowings and finance lease liabilities               | 338  |      |            |
                9. Convertible bonds                                                | 339  |      |            |
                10. Preference shares                                               | 340  |      |            |
                11. Deferred income tax payables                                    | 341  |      |            |
                12. Long-term provisions                                            | 342  |      |            |
                13. Science and technology development fund                         | 343  |      |            |
        Total D - OWNER’S EQUITY (400 = 410 + 430)                                  | 400  |      |            |
            Total I. Owner’s equity                                                 | 410  |      |            |
            (410 = 411 + 412 + 413 + 414 + 415 + 416                                |      |      |            |
            + 417 + 418 + 419 + 420 + 421 + 422)                                    |      |      |            |
                Total 1. Contributed capital                                        | 411  |      |            |
                    - Ordinary shares with voting rights                            | 411a |      |            |
                    - Preference shares                                             | 411b |      |            |
                2. Capital surplus                                                  | 412  |      |            |
                3. Conversion options on convertible bonds                          | 413  |      |            |
                4. Other capital                                                    | 414  |      |            |
                5. Treasury shares                                                  | 415  |      |            |
                6. Differences upon asset revaluation                               | 416  |      |            |
                7. Exchange rate differences                                        | 417  |      |            |
                8. Development and investment funds                                 | 418  |      |            |
                9. Enterprise reorganization assistance fund                        | 419  |      |            |
                10. Other equity funds                                              | 420  |      |            |
                Total 11. Undistributed profit after tax                            | 421  |      |            |
                    - Undistributed profit after tax brought forward                | 421a |      |            |
                    - Undistributed profit after tax for the current year           | 421b |      |            |
                12. Capital expenditure funds                                       | 422  |      |            |
            Total II. Funding sources and other funds (430 = 431 + 432)             | 430  |      |            |
                1. Funding sources                                                  | 431  |      |            |
                2. Funds used for fixed asset acquisition                           | 432  |      |            |
        TOTAL EQUITY (440 = 300 + 400)                                              | 440  |      |            |
        ----------------------------------------------------------------------------|------|------|------------|
        """

        # 15/12/2020 5,000,000 in cash as a capital contribution
        journal_items_1 = [{
            'account_id': self.default_account_1111.id,
            'debit': 5000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_41111.id,
            'debit': 0,
            'credit': 5000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_1)

        # 01/12/2020 Make a cash deposit into account 4,000,000.
        journal_items_2 = [{
            'account_id': self.default_account_1121.id,
            'debit': 4000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 4000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_2)

        # 25/12/2020 Buy foreign currency with VND account, transfer to USD account, foreign currency amount: 50 000 USD exchange rate 1 USD = 23,000 VND.
        journal_items_3 = [{
            'account_id': self.default_account_1122.id,
            'debit': 1150000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 1150000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 25, 12, 0), self.default_journal_vn_misc, items=journal_items_3)

        # 10/12/2020
        journal_items_4 = [{
            'account_id': self.default_account_1211.id,
            'debit': 450000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 450000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_4)

        # 05/12/2020
        journal_items_5 = [{
            'account_id': self.default_account_1281.id,
            'debit': 300000,
            'credit': 0,
            'date_maturity': date(2021, 2, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 300000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_5)

        # 05/12/2020
        journal_items_6 = [{
            'account_id': self.default_account_1281.id,
            'debit': 500000,
            'credit': 0,
            'date_maturity': date(2021, 9, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_6)

        # 05/12/2020
        journal_items_7 = [{
            'account_id': self.default_account_1281.id,
            'debit': 500000,
            'credit': 0,
            'date_maturity': date(2022, 12, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_7)

        # 05/12/2020
        journal_items_8 = [{
            'account_id': self.default_account_331.id,
            'debit': 550000,
            'credit': 0,
            'partner_id': self.vendor_c.id,
            'date_maturity': date(2020, 12, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 550000,
        }]
        self._init_journal_entry(self.vendor_c, datetime(2020, 12, 5, 12, 0), self.default_journal_vn_bank, items=journal_items_8)

        # 05/12/2020
        journal_items_9 = [{
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 1100000,
            'partner_id': self.vendor_c.id,
            'date_maturity': date(2021, 1, 15),
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 1000000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 100000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        self._init_journal_entry(self.vendor_c, datetime(2020, 12, 6, 12, 0), self.default_journal_vn_bank, items=journal_items_9)

        # 05/12/2020
        journal_items_10 = [{
            'account_id': self.default_account_331.id,
            'debit': 550000,
            'credit': 0,
            'partner_id': self.vendor_c.id,
            'date_maturity': date(2022, 12, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 550000,
        }]
        self._init_journal_entry(self.vendor_c, datetime(2020, 12, 5, 12, 0), self.default_journal_vn_bank, items=journal_items_10)

        # 07/12/2020
        journal_items_11_01 = [{
            'account_id': self.default_account_131.id,
            'debit': 1100000,
            'credit': 0,
            'partner_id': self.customer_a.id,
            'date_maturity': date(2021, 1, 21),
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 1000000,
            'tax_ids': [(6, 0, self.tax_price_vn_sale_10.ids)]
        },
        {
            'account_id': self.default_account_33311.id,
            'debit': 0,
            'credit': 100000,
            'tax_repartition_line_id': self.tax_repartition_line_vn_sale_10.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 7, 12, 0), self.default_journal_vn_misc, items=journal_items_11_01)

        journal_items_11_02 = [{
            'account_id': self.default_account_632.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 7, 12, 0), self.default_journal_vn_misc, items=journal_items_11_02)

        journal_items_11_03 = [{
            'account_id': self.default_account_5111.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 7, 12, 0), self.default_journal_vn_misc, items=journal_items_11_03)

        journal_items_11_04 = [{
            'account_id': self.default_account_911.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 0,
            'credit': 500000,
        },
        {
            'account_id': self.default_account_4212.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 7, 12, 0), self.default_journal_vn_misc, items=journal_items_11_04)

        # 07/12/2020
        journal_items_12 = [{
            'account_id': self.default_account_1121.id,
            'debit': 550000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 550000,
            'date_maturity': date(2020, 12, 7),
            'partner_id': self.customer_a.id,
        }]
        self._init_journal_entry(self.customer_a, datetime(2020, 12, 7, 12, 0), self.default_journal_vn_bank, items=journal_items_12)

        # 24/12/2020
        journal_items_13 = [{
            'account_id': self.default_account_337.id,
            'debit': 200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 200000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 24, 12, 0), self.default_journal_vn_misc, items=journal_items_13)

        # 14/12/2020
        journal_items_14 = [{
            'account_id': self.default_account_1283.id,
            'debit': 50000,
            'credit': 0,
            'date_maturity': date(2021, 6, 14),
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 50000,
            'partner_id': self.customer_a.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 14, 12, 0), self.default_journal_vn_misc, items=journal_items_14)

        # 10/12/2020
        journal_items_15 = [{
            'account_id': self.default_account_141.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.customer_a.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_15)

        # 31/12/2020
        journal_items_16 = [{
            'account_id': self.default_account_6426.id,
            'debit': 25000,
            'credit': 0,
            'date_maturity': date(2021, 6, 30),
        },
        {
            'account_id': self.default_account_2293.id,
            'debit': 0,
            'credit': 25000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_16)

        # 31/12/2020
        journal_items_17 = [{
            'account_id': self.default_account_1381.id,
            'debit': 1000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 0,
            'credit': 1000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_17)

        # 31/12/2020
        journal_items_18 = [{
            'account_id': self.default_account_6426.id,
            'debit': 80000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2294.id,
            'debit': 0,
            'credit': 80000,
            'date_maturity': date(2021, 6, 30),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_18)

        # 31/12/2020
        journal_items_19 = [{
            'account_id': self.default_account_242.id,
            'debit': 120000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_short_term_prepaid_expense.ids)]
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 120000,
        },
        {
            'account_id': self.default_account_242.id,
            'debit': 360000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_long_term_prepaid_expense.ids)]
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 360000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_19)

        # 20/12/2020
        journal_items_20 = [{
            'account_id': self.default_account_1368.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_20)

        # 20/12/2020
        journal_items_21 = [{
            'account_id': self.default_account_171.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_21)

        # 20/12/2020
        journal_items_22 = [{
            'account_id': self.default_account_2288.id,
            'debit': 200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 200000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_22)

        # 20/12/2020
        journal_items_23 = [{
            'account_id': self.default_account_131.id,
            'debit': 550000,
            'credit': 0,
            'partner_id': self.customer_a.id,
            'date_maturity': date(2022, 1, 1),
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 500000,
            'tax_ids': [(6, 0, self.tax_price_vn_sale_10.ids)]
        },
        {
            'account_id': self.default_account_33311.id,
            'debit': 0,
            'credit': 50000,
            'tax_repartition_line_id': self.tax_repartition_line_vn_sale_10.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_23)

        # 20/12/2020
        journal_items_24 = [{
            'account_id': self.default_account_1368.id,
            'debit': 20000,
            'credit': 0,
            'date_maturity': date(2022, 6, 30),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 20000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_24)

        # 20/12/2020
        journal_items_25 = [{
            'account_id': self.default_account_1361.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_25)

        # 20/12/2020
        journal_items_26 = [{
            'account_id': self.default_account_1283.id,
            'debit': 40000,
            'credit': 0,
            'partner_id': self.customer_a.id,
            'date_maturity': date(2022, 12, 19),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 40000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_26)

        # 20/12/2020
        journal_items_27 = [{
            'account_id': self.default_account_1388.id,
            'debit': 30000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
            'date_maturity': date(2023, 12, 20),
        },
        {
            'account_id': self.default_account_2111.id,
            'debit': 0,
            'credit': 30000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_27)

        # 20/12/2020
        journal_items_28 = [{
            'account_id': self.default_account_6426.id,
            'debit': 80000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2293.id,
            'debit': 0,
            'credit': 80000,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_28)

        # 01/12/2020
        journal_items_29 = [{
            'account_id': self.default_account_2112.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_6424.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2141.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_29)

        # 01/12/2020
        journal_items_30 = [{
            'account_id': self.default_account_2121.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2142.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_30)

        # 01/12/2020
        journal_items_31 = [{
            'account_id': self.default_account_2131.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_6424.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2143.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_31)

        # 01/12/2020
        journal_items_32 = [{
            'account_id': self.default_account_217.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2147.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_32)

        # 31/12/2020
        journal_items_33 = [{
            'account_id': self.default_account_635.id,
            'debit': 2500,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2291.id,
            'debit': 0,
            'credit': 2500,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_33)

        # 31/12/2020
        journal_items_34 = [{
            'account_id': self.default_account_6426.id,
            'debit': 25000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2294.id,
            'debit': 0,
            'credit': 25000,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_34)

        # 31/12/2020
        journal_items_35 = [{
            'account_id': self.default_account_2412.id,
            'debit': 45000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 45000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_35)

        # 31/12/2020
        journal_items_36 = [{
            'account_id': self.default_account_221.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_36)

        # 31/12/2020
        journal_items_37 = [{
            'account_id': self.default_account_222.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_37)

        # 31/12/2020
        journal_items_38 = [{
            'account_id': self.default_account_2281.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_38)

        # 31/12/2020
        journal_items_39 = [{
            'account_id': self.default_account_6426.id,
            'debit': 20000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2292.id,
            'debit': 0,
            'credit': 20000,
            'date_maturity': date(2025, 12, 31),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_39)

        # 20/12/2020
        journal_items_40 = [{
            'account_id': self.default_account_243.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_8212.id,
            'debit': 0,
            'credit': 15000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_40)

        # 10/12/2018
        journal_items_41 = [{
            'account_id': self.default_account_2288.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2018, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_41)

        # 31/12/2020
        journal_items_43 = [{
            'account_id': self.default_account_6421.id,
            'debit': 18000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3341.id,
            'debit': 0,
            'credit': 18000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_43)

        # 31/12/2020
        journal_items_44 = [{
            'account_id': self.default_account_6421.id,
            'debit': 3780,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3383.id,
            'debit': 0,
            'credit': 3060,
        },
        {
            'account_id': self.default_account_3384.id,
            'debit': 0,
            'credit': 540,
        },
        {
            'account_id': self.default_account_3386.id,
            'debit': 0,
            'credit': 180,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_44)

        # 31/12/2020
        journal_items_45 = [{
            'account_id': self.default_account_6427.id,
            'debit': 5000,
            'credit': 0,
            'date_maturity': date(2021, 1, 10),
        },
        {
            'account_id': self.default_account_335.id,
            'debit': 0,
            'credit': 5000,
            'date_maturity': date(2021, 1, 10),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_45)

        # 10/12/2020
        journal_items_46 = [{
            'account_id': self.default_account_6427.id,
            'debit': 5000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 5000,
            'partner_id': self.vendor_a.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_46)

        journal_items_46_01 = [{
            'account_id': self.default_account_331.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_46_01)

        # 24/12/2020
        journal_items_47 = [{
            'account_id': self.default_account_131.id,
            'debit': 200000,
            'credit': 0,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2021, 3, 31),
        },
        {
            'account_id': self.default_account_337.id,
            'debit': 0,
            'credit': 200000,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2021, 3, 31),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 24, 12, 0), self.default_journal_vn_misc, items=journal_items_47)

        # 01/12/2020
        journal_items_48 = [{
            'account_id': self.default_account_131.id,
            'debit': 240000,
            'credit': 0,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2021, 2, 28),
        },
        {
            'account_id': self.default_account_3387.id,
            'debit': 0,
            'credit': 240000,
            'partner_id': self.customer_b.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_48)

        # 15/12/2020
        journal_items_49 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3411.id,
            'debit': 0,
            'credit': 1000000,
            'date_maturity': date(2021, 3, 15),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_49)

        # 15/12/2020
        journal_items_50 = [{
            'account_id': self.default_account_6415.id,
            'debit': 16000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3521.id,
            'debit': 0,
            'credit': 16000,
            'date_maturity': date(2021, 3, 31),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_50)

        # 15/12/2020
        journal_items_51 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3531.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_51)

        # 15/12/2020
        journal_items_52 = [{
            'account_id': self.default_account_632.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_357.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_52)

        # 15/12/2020
        journal_items_53 = [{
            'account_id': self.default_account_1121.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_171.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_53)

        # 31/12/2020
        journal_items_56 = [{
            'account_id': self.default_account_635.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_335.id,
            'debit': 0,
            'credit': 10000,
            'date_maturity': date(2022, 2, 28),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_56)

        # 20/12/2020
        journal_items_57 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3361.id,
            'debit': 0,
            'credit': 1000000,
            'date_maturity': date(2022, 12, 20),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_57)

        # 06/12/2020
        journal_items_54 = [{
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 1100000,
            'partner_id': self.vendor_a.id,
            'date_maturity': date(2022, 1, 15),
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 1000000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 100000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 6, 12, 0), self.default_journal_vn_misc, items=journal_items_54)

        # 10/12/2020
        journal_items_58_01 = [{
            'account_id': self.default_account_6427.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.vendor_a.id,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(self.customer_b, datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_58_01)

        journal_items_58_02 = [{
            'account_id': self.default_account_331.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
            'date_maturity': date(2022, 12, 31),
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 10000,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(self.customer_b, datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_58_02)

        # 01/12/2020
        journal_items_59 = [{
            'account_id': self.default_account_131.id,
            'debit': 240000,
            'credit': 0,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2022, 12, 1),
        },
        {
            'account_id': self.default_account_3387.id,
            'debit': 0,
            'credit': 240000,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2022, 12, 1),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_59)

        # 01/12/2020
        journal_items_60 = [{
            'account_id': self.default_account_1121.id,
            'debit': 2000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_344.id,
            'debit': 0,
            'credit': 2000,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2022, 12, 1),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_60)

        # 15/12/2020
        journal_items_62 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3432.id,
            'debit': 0,
            'credit': 1000000,
            'date_maturity': date(2022, 6, 15),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_62)

        # 15/12/2020
        journal_items_61 = [{
            'account_id': self.default_account_1121.id,
            'debit': 10000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3411.id,
            'debit': 0,
            'credit': 10000000,
            'date_maturity': date(2023, 12, 15),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_61)

        # 15/12/2020
        journal_items_63 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1300000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_41111.id,
            'debit': 0,
            'credit': 700000,
        },
        {
            'account_id': self.default_account_4112.id,
            'debit': 0,
            'credit': 100000,
        },
        {
            'account_id': self.default_account_41112.id,
            'debit': 0,
            'credit': 150000,
        },
        {
            'account_id': self.default_account_41112.id,
            'debit': 0,
            'credit': 150000,
        },
        {
            'account_id': self.default_account_4112.id,
            'debit': 0,
            'credit': 200000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_63)

        # 20/12/2020
        journal_items_64 = [{
            'account_id': self.default_account_8212.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_347.id,
            'debit': 0,
            'credit': 15000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_64)

        # 15/12/2020
        journal_items_65 = [{
            'account_id': self.default_account_6415.id,
            'debit': 16000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3521.id,
            'debit': 0,
            'credit': 16000,
            'date_maturity': date(2022, 3, 31),
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_65)

        # 15/12/2020
        journal_items_66 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3561.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_66)

        # 15/12/2020
        journal_items_67 = [{
            'account_id': self.default_account_3432.id,
            'debit': 1000000,
            'credit': 0,
            'date_maturity': date(2022, 6, 15),
        },
        {
            'account_id': self.default_account_4113.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_67)

        # 15/12/2020
        journal_items_68 = [{
            'account_id': self.default_account_1121.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4118.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_68)

        # 15/12/2020
        journal_items_69 = [{
            'account_id': self.default_account_419.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_69)

        # 31/12/2020
        journal_items_70 = [{
            'account_id': self.default_account_2111.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_412.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_70)

        # 31/12/2020
        journal_items_72 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_414.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_72)

        # 15/12/2020
        journal_items_73 = [{
            'account_id': self.default_account_1385.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_417.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_73)

        # 15/12/2020
        journal_items_74 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_418.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_74)

        # 01/01/2020
        journal_items_75 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4211.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None, datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_75)

        # 01/01/2020
        journal_items_76 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_441.id,
            'debit': 0,
            'credit': 1500000,
        }]
        self._init_journal_entry(None, datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_76)

        # 01/01/2020
        journal_items_77 = [{
            'account_id': self.default_account_441.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None, datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_77)

        # 01/01/2020
        journal_items_78 = [{
            'account_id': self.default_account_1121.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4612.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None, datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_78)

        # 01/01/2020
        journal_items_79 = [{
            'account_id': self.default_account_2112.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4612.id,
            'debit': 0,
            'credit': 30000,
        },
        {
            'account_id': self.default_account_1612.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_466.id,
            'debit': 0,
            'credit': 30000,
        }]
        self._init_journal_entry(None, datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_79)

        # 31/12/2020
        journal_items_80 = [{
            'account_id': self.default_account_5111.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 0,
            'credit': 700000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 0,
            'credit': 120000,
        },
        {
            'account_id': self.default_account_635.id,
            'debit': 0,
            'credit': 12500,
        },
        {
            'account_id': self.default_account_6415.id,
            'debit': 0,
            'credit': 32000,
        },
        {
            'account_id': self.default_account_6421.id,
            'debit': 0,
            'credit': 21780,
        },
        {
            'account_id': self.default_account_6424.id,
            'debit': 0,
            'credit': 20000,
        },
        {
            'account_id': self.default_account_6426.id,
            'debit': 0,
            'credit': 230000,
        },
        {
            'account_id': self.default_account_6427.id,
            'debit': 0,
            'credit': 20000,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 456280,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 243720,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4212.id,
            'debit': 0,
            'credit': 243720,
        }]
        self._init_journal_entry(None, datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_80)

        lines_to_check = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2020, 12, 31, 0, 0), filter_option='custom', date_from=datetime(2020, 1, 1, 0, 0), date_to=datetime(2020, 12, 31, 0, 0), cash_basis=False)

        # Check Total ASSETS Equal Total EQUITY
        self._check_balance_sheet(
            lines_to_check,
            '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01').id,
            '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02').id
        )

        lines_expected_value = [{
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01').id,
                'name': 'TOTAL ASSETS (270 = 100 + 200)',
                'columns': {'balance': 25104500.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01').id,
                'name': 'A - CURRENT ASSETS (100 = 110 + 120 + 130 + 140 + 150)',
                'columns': {'balance': 13934500.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_01').id,
                'name': 'I. Cash and Cash Equivalents (110 = 111 + 112)',
                'columns': {'balance': 8627000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_01_01').id,
                'name': '1. Bank & Cash',
                'columns': {'balance': 8327000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_01_02').id,
                'name': '2. Cash equivalents',
                'columns': {'balance': 300000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_02').id,
                'name': 'II. Short-term financial investments (120 = 121 + 122 + 123)',
                'columns': {'balance': 947500.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_02_01').id,
                'name': '1. Trading securities',
                'columns': {'balance': 450000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_02_02').id,
                'name': '2. Allowances for decline in value of trading securities',
                'columns': {'balance': -2500.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_02_03').id,
                'name': '3. Held to maturity investments',
                'columns': {'balance': 500000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03').id,
                'name': 'III. Short-term receivables (130 = 131 + 132 + 133 + 134 + 135 + 136 + 137 + 139)',
                'columns': {'balance': 2446000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_01').id,
                'name': '1. Short-term trade receivables',
                'columns': {'balance': 1540000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_02').id,
                'name': '2. Short-term prepayments to suppliers',
                'columns': {'balance': 560000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_03').id,
                'name': '3. Short-term intra-company receivables',
                'columns': {'balance': 10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_04').id,
                'name': '4. Receivables under schedule of construction contract',
                'columns': {'balance': 200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_05').id,
                'name': '5. Short-term loan receivables',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_06').id,
                'name': '6. Other short-term receivables',
                'columns': {'balance': 110000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_07').id,
                'name': '7. Short-term allowances for doubtful debts',
                'columns': {'balance': -25000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_03_08').id,
                'name': '8. Shortage of assets awaiting resolution',
                'columns': {'balance': 1000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_04').id,
                'name': 'IV. Inventories (140 = 141 + 149)',
                'columns': {'balance': 1594000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_04_01').id,
                'name': '1. Inventories',
                'columns': {'balance': 1699000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_04_01_01').id,
                'name': '1.a. All Inventories',
                'columns': {'balance': 1699000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_04_01_02').id,
                'name': '1.b. Minus Long-term work in progress',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_04_01_03').id,
                'name': '1.c. Minus Long-term equipment and spare parts for replacement',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_04_02').id,
                'name': '2. Allowances for decline in value of inventories',
                'columns': {'balance': -105000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_05').id,
                'name': 'V. Other current assets (150 = 151 + 152 + 153 + 154 + 155)',
                'columns': {'balance': 320000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_05_01').id,
                'name': '1. Short-term prepaid expenses',
                'columns': {'balance': 120000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_05_02').id,
                'name': '2. Deductible VAT',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_05_03').id,
                'name': '3. Taxes and other receivables from government budget',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_05_04').id,
                'name': '4. Government bonds purchased for resale',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_01_05_05').id,
                'name': '5. Other current assets',
                'columns': {'balance': 200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02').id,
                'name': 'B - NON-CURRENT ASSETS (200 = 210 + 220 + 240 + 250 + 260)',
                'columns': {'balance': 11170000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01').id,
                'name': 'I. Long-term receivables (210 = 211 + 212 + 213 + 214 + 215 + 216 + 219)',
                'columns': {'balance': 2360000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_01').id,
                'name': '1. Long-term trade receivables',
                'columns': {'balance': 790000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_02').id,
                'name': '2. Long-term prepayments to suppliers',
                'columns': {'balance': 560000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_03').id,
                'name': '3. Working capital provided to sub-units',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_04').id,
                'name': '4. Long-term intra-company receivables',
                'columns': {'balance': 20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_05').id,
                'name': '5. Long-term loan receivables',
                'columns': {'balance': 40000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_06').id,
                'name': '6. Other long-term receivables',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_06_01').id,
                'name': '6a. Other long-term receivables (assets)',
                'columns': {'balance': 30000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_06_02').id,
                'name': '6b. Other long-term receivables (equity)',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_01_07').id,
                'name': '7. Long-term allowances for doubtful debts',
                'columns': {'balance': -80000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02').id,
                'name': 'II. Fixed assets (220 = 221 + 224 + 227 + 230)',
                'columns': {'balance': 4810000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_01').id,
                'name': '1. Tangible fixed assets (221 = 222 + 223)',
                'columns': {'balance': 1240000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_01_01').id,
                'name': '- Historical costs',
                'columns': {'balance': 1250000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_01_02').id,
                'name': '- Accumulated depreciation',
                'columns': {'balance': -10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_02').id,
                'name': '2. Finance lease fixed assets (224 = 225 + 226)',
                'columns': {'balance': 1190000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_02_01').id,
                'name': '- Historical costs',
                'columns': {'balance': 1200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_02_02').id,
                'name': '- Accumulated depreciation',
                'columns': {'balance': -10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_03').id,
                'name': '3. Intangible fixed assets (227 = 228 + 229)',
                'columns': {'balance': 1190000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_03_01').id,
                'name': '- Historical costs',
                'columns': {'balance': 1200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_02_03_02').id,
                'name': '- Accumulated depreciation',
                'columns': {'balance': -10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_03').id,
                'name': 'III. Investment properties (230 = 231 + 232)',
                'columns': {'balance': 1190000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_03_01').id,
                'name': '- Historical costs',
                'columns': {'balance': 1200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_03_02').id,
                'name': '- Accumulated depreciation',
                'columns': {'balance': -10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_04').id,
                'name': 'IV. Long-term assets in progress (240 = 241 + 242)',
                'columns': {'balance': 45000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_04_01').id,
                'name': '1. Long-term work in progress',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_04_02').id,
                'name': '2. Construction in progress',
                'columns': {'balance': 45000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_05').id,
                'name': 'V. Long-term investments (250 = 251 + 252 + 253 + 254 + 255)',
                'columns': {'balance': 3480000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_05_01').id,
                'name': '1. Investments in subsidiaries',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_05_02').id,
                'name': '2. Investments in joint ventures and associates',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_05_03').id,
                'name': '3. Investments in equity of other entities',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_05_04').id,
                'name': '4. Allowances for long-term investments',
                'columns': {'balance': -20000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_05_05').id,
                'name': '5. Held to maturity investments',
                'columns': {'balance': 500000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_06').id,
                'name': 'VI. Other long-term assets (260 = 261 + 262 + 263 + 268)',
                'columns': {'balance': 475000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_06_01').id,
                'name': '1. Long-term prepaid expenses',
                'columns': {'balance': 360000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_06_02').id,
                'name': '2. Deferred income tax assets',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_06_03').id,
                'name': '3. Long-term equipment and spare parts for replacement',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_01_02_06_04').id,
                'name': '4. Other long-term assets',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02').id,
                'name': 'TOTAL EQUITY (440 = 300 + 400)',
                'columns': {'balance': 25104500, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01').id,
                'name': 'C - LIABILITIES (300 = 310 + 330)',
                'columns': {'balance': 15880780.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01').id,
                'name': 'I. Short-term liabilities (310 = 311 + 312 + 313 + 314 + 315 + 316 + 317 + 318 + 319 + 320 + 321 + 322 + 323 + 324)',
                'columns': {'balance': 3387780.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_01').id,
                'name': '1. Short-term trade payables',
                'columns': {'balance': 1105000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_02').id,
                'name': '2. Short-term prepayments from customers',
                'columns': {'balance': 550000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_03').id,
                'name': '3. Taxes and other payables to government budget',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_04').id,
                'name': '4. Payables to employees',
                'columns': {'balance': 18000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_05').id,
                'name': '5. Short-term accrued expenses',
                'columns': {'balance': 5000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_06').id,
                'name': '6. Short-term intra-company payables',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_07').id,
                'name': '7. Payables under schedule of construction contract',
                'columns': {'balance': 200000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_08').id,
                'name': '8. Short-term unearned revenues',
                'columns': {'balance': 240000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_09').id,
                'name': '9. Other short-term payments',
                'columns': {'balance': 3780.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_10').id,
                'name': '10. Short-term borrowings and finance lease liabilities',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_11').id,
                'name': '11. Short-term provisions',
                'columns': {'balance': 16000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_12').id,
                'name': '12. Bonus and welfare fund',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_13').id,
                'name': '13. Price stabilization fund',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_01_14').id,
                'name': '14. Government bonds purchased for resale',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02').id,
                'name': 'II. Long-term liabilities (330 = 331 + 332 + 333 + 334 + 335 + 336 + 337 + 338 + 339 + 340 + 341 + 342 + 343)',
                'columns': {'balance': 12493000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_01').id,
                'name': '1. Long-term trade payables',
                'columns': {'balance': 1110000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_02').id,
                'name': '2. Long-term prepayments from customers',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_03').id,
                'name': '3. Long-term accrued expenses',
                'columns': {'balance': 10000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_04').id,
                'name': '4. Intra-company payables for operating capital received',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_05').id,
                'name': '5. Long-term intra-company payables',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_06').id,
                'name': '6. Long-term unearned revenues',
                'columns': {'balance': 240000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_07').id,
                'name': '7. Other long-term payables',
                'columns': {'balance': 2000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_08').id,
                'name': '8. Long-term borrowings and finance lease liabilities',
                'columns': {'balance': 10000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_08_01').id,
                'name': '8a. Long-term borrowings and finance lease liabilities (via Credit Balance)',
                'columns': {'balance': 10000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_08_02').id,
                'name': '8b. Long-term borrowings and finance lease liabilities (via Debit Balance)',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_09').id,
                'name': '9. Convertible bonds',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_10').id,
                'name': '10. Preference shares',
                'columns': {'balance': -0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_11').id,
                'name': '11. Deferred income tax payables',
                'columns': {'balance': 15000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_12').id,
                'name': '12. Long-term provisions',
                'columns': {'balance': 16000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_01_02_13').id,
                'name': '13. Science and technology development fund',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02').id,
                'name': 'D - OWNER’S EQUITY (400 = 410 + 430)',
                'columns': {'balance': 9223720.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01').id,
                'name': 'I. Owner’s equity (410 = 411 + 412 + 413 + 414 + 415 + 416 + 417 + 418 + 419 + 420 + 421 + 422)',
                'columns': {'balance': 9143720.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_01').id,
                'name': '1. Contributed capital',
                'columns': {'balance': 6000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_01_01').id,
                'name': '- Ordinary shares with voting rights',
                'columns': {'balance': 5700000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_01_02').id,
                'name': '- Preference shares',
                'columns': {'balance': 300000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_02').id,
                'name': '2. Capital surplus',
                'columns': {'balance': 300000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_03').id,
                'name': '3. Conversion options on convertible bonds',
                'columns': {'balance': 1000000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_04').id,
                'name': '4. Other capital',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_05').id,
                'name': '5. Treasury shares',
                'columns': {'balance': -500000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_06').id,
                'name': '6. Differences upon asset revaluation',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_07').id,
                'name': '7. Exchange rate differences',
                'columns': {'balance': 0.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_08').id,
                'name': '8. Development and investment funds',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_09').id,
                'name': '9. Enterprise reorganization assistance fund',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_10').id,
                'name': '10. Other equity funds',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_11').id,
                'name': '11. Undistributed profit after tax',
                'columns': {'balance': 493720.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_11_01').id,
                'name': '- Undistributed profit after tax brought forward',
                'columns': {'balance': 100000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_11_02').id,
                'name': '- Undistributed profit after tax for the current year',
                'columns': {'balance': 393720.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_01_12').id,
                'name': '12. Capital expenditure funds',
                'columns': {'balance': 1450000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_02').id,
                'name': 'II. Funding sources and other funds (430 = 431 + 432)',
                'columns': {'balance': 80000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_02_01').id,
                'name': '1. Funding sources',
                'columns': {'balance': 50000.0, }
            },
            {
                'id': '~account.report.line~%s' % self.env.ref('l10n_vn_viin_account_reports.balance_sheet_c200_line_02_02_02_02').id,
                'name': '2. Funds used for fixed asset acquisition',
                'columns': {'balance': 30000.0, }
            },
        ]
        self._check_report_value(lines_to_check, lines_expected_value)
