from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    report_paperformat_ads_vn = env.ref('l10n_vn_viin_account_reports.report_paperformat_ads_vn_euro_landscape', False)
    if report_paperformat_ads_vn:
        report_paperformat_ads_vn.margin_bottom = 25
