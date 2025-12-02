from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    to_gl_vn_report_paperformat_euro_landscape_id = env.ref('to_l10n_vn_general_ledger.to_gl_vn_report_paperformat_euro_landscape', raise_if_not_found=False)
    if to_gl_vn_report_paperformat_euro_landscape_id:
        to_gl_vn_report_paperformat_euro_landscape_id.write({
            'orientation': 'Portrait',
            'margin_top': 30,
            'header_spacing': 25,
            })
