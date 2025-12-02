from odoo.tests.common import tagged

from odoo.addons.to_account_reports.tests.common import AccountReportsCommon
from odoo.tools.misc import NON_BREAKING_SPACE


@tagged('post_install', '-at_install', 'post_install_l10n')
class AccountReportL10nVn(AccountReportsCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_vn.vn_template'):
        super(AccountReportL10nVn, cls).setUpClass(chart_template_ref=chart_template_ref)

        accounts_vn = cls.env['account.account'].search([('company_id', '=', cls.company_data['company'].id)])
        cls.default_account_1125 = accounts_vn.filtered(lambda r: r.code == '1125')
        cls.default_account_1126 = accounts_vn.filtered(lambda r: r.code == '1126')

        company_data_vn = cls.company_data
        # Default account for journal entry (exp: cls.default_account_347)
        for key, val in company_data_vn['accounts'].items():
            setattr(cls, key, val)

        # Default journal for journal entry
        cls.default_journal_vn_misc = company_data_vn['default_journal_misc']
        cls.default_journal_vn_sale = company_data_vn['default_journal_sale']
        cls.default_journal_vn_purchase = company_data_vn['default_journal_purchase']
        cls.default_journal_vn_bank = company_data_vn['default_journal_bank']
        cls.default_journal_vn_cash = company_data_vn['default_journal_cash']

        # Default tax
        cls.tax_price_vn_purchase_5 = cls.env['account.tax'].create({
            'name': '5% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_vn_purchase_5 = cls.tax_price_vn_purchase_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_vn_purchase_10 = cls.env['account.tax'].create({
            'name': '10% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_vn_purchase_10 = cls.tax_price_vn_purchase_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_vn_sale_5 = cls.env['account.tax'].create({
            'name': '5% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_vn_sale_5 = cls.tax_price_vn_sale_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_vn_sale_10 = cls.env['account.tax'].create({
            'name': '10% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_vn_sale_10 = cls.tax_price_vn_sale_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        # Account Analytic Tag
        cls.analytic_tag_short_term_prepaid_expense = cls.env.ref('viin_analytic_tag.account_analytic_tag_short_term_prepaid_expense')
        cls.analytic_tag_long_term_prepaid_expense = cls.env.ref('viin_analytic_tag.account_analytic_tag_long_term_prepaid_expense')
        cls.analytic_tag_fixed_assets = cls.env.ref('viin_analytic_tag.account_analytic_tag_fixed_assets')
        cls.analytic_tag_liquidation_fixed_assets = cls.env.ref('viin_analytic_tag.account_analytic_tag_liquidation_assets')
        cls.analytic_tag_interests_dividends_distributed_profits = cls.env.ref('viin_analytic_tag.account_analytic_tag_interests_dividends_distributed_profits')
        cls.analytic_tag_borrowing_loan = cls.env.ref('viin_analytic_tag.account_analytic_tag_borrowing_loan')
        cls.analytic_tag_lending_loan = cls.env.ref('viin_analytic_tag.account_analytic_tag_lending_loan')

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        """ Create a new company having the name passed as parameter.
        A chart of accounts will be installed to this company: the same as the current company one.
        The current user will get access to this company.

        :param company_name (str) : The name of the company.
        :param chart_template (record) : The chart template.
        :return: A dictionary will be returned containing all relevant accounting data for testing.
        """
        company_data = super().setup_company_data(company_name, chart_template=chart_template, **kwargs)

        vnd = cls.env.ref('base.VND')
        if not vnd.active:
            vnd.active = True
        company_data['company'].currency_id = vnd

        company = company_data['company']
        chart_account = cls.env['account.account'].search([('company_id', '=', company.id)])
        account_journal = cls.env['account.journal'].search([('company_id', '=', company.id)])
        company_vals = {
            'company': company,
            'currency': company.currency_id,
            'default_journal_misc': account_journal.filtered(lambda p: p.type == 'general')[:1],
            'default_journal_sale': account_journal.filtered(lambda p: p.type == 'sale')[:1],
            'default_journal_purchase': account_journal.filtered(lambda p: p.type == 'purchase')[:1],
            'default_journal_bank': account_journal.filtered(lambda p: p.type == 'bank')[:1],
            'default_journal_cash': account_journal.filtered(lambda p: p.type == 'cash')[:1],
        }
        # Accounts should be added to the company's value.
        # Return exp: 'default_journal_1111': account.account(111,)
        accounts = {}
        for account in chart_account:
            key = 'default_account_' + account.code
            accounts.update({
                key: cls._filtered_account(chart_account, chart_template, [('code', '=', account.code)])
            })
        if accounts:
            company_vals.update({'accounts': accounts})
        company_data.update(company_vals)

        return company_data

    def _prepare_output_value(self, block_value, output_value):
        output_value = super(AccountReportL10nVn, self)._prepare_output_value(block_value, output_value)
        for vn_currency_symbol in ['đ', '₫']:
            if vn_currency_symbol in block_value:
                index = output_value.find('.')
                output_value = '%s%s%s' % (output_value[0:index], NON_BREAKING_SPACE, vn_currency_symbol)
        return output_value
