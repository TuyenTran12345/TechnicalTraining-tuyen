from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_vn.vn_template').write({
        'account_report_footer_layout': 'to_l10n_vn_qweb_layout.accounting_external_footer_layout',
        })
