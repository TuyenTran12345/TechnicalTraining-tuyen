from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    xmlids_del = (
        'ccash_flow_c200_line_01_02_02_exp_01',
    )
    for xml_id in xmlids_del:
        report_line_to_del = env.ref('l10n_vn_viin_account_reports.%s' % xml_id, raise_if_not_found=False)
        if report_line_to_del:
            report_line_to_del.unlink()
