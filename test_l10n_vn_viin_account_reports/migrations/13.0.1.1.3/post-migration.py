from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vn_template = env.ref('l10n_vn.vn_template', False)
    if vn_template:
        env['account.account.template']._apply_show_both_dr_and_cr_trial_balance()
        env['account.account']._apply_show_both_dr_and_cr_trial_balance()
