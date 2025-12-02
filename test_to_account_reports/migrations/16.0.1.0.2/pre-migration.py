from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    profit_and_loss_line_02_01_02 = env.ref('to_account_reports.profit_and_loss_line_02_01_02', raise_if_not_found=False)
    if profit_and_loss_line_02_01_02:
        profit_and_loss_line_02_01_02.unlink()

    profit_and_loss_line_02_01_02_expr_01 = env.ref('to_account_reports.profit_and_loss_line_02_01_02_expr_01', raise_if_not_found=False)
    if profit_and_loss_line_02_01_02_expr_01:
        profit_and_loss_line_02_01_02_expr_01.unlink()
