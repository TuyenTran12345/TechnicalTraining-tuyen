from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    xmlids_del = (
        'cash_flow_c200_report',
        'cash_flow_c133_report',
        'profit_and_loss_c200_report',
        'profit_and_loss_c133_report'
    )
    for xml_id in xmlids_del:
        report_line_to_del = env.ref('l10n_vn_viin_account_reports.%s' % xml_id, raise_if_not_found=False)
        if report_line_to_del:
            report_line_to_del.unlink()
