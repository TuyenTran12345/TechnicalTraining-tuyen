from odoo import fields, models


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    af_report_render_print_template = fields.Char(string='Account Report Print PDF Template', default='l10n_vn_viin_account_reports.main_template_print_vn',
                                                  help="This template is only used when printing a financial report to a PDF output")
    coa_report_print_template = fields.Char(string='Trial Balance Report Print PDF Template', default='l10n_vn_viin_account_reports.template_coa_report_print_vn')
    af_report_header_layout = fields.Char(string='Account Report Print PDF Header Layout', default='l10n_vn_viin_account_reports.header_template_print_vn')
    af_report_footer_layout = fields.Char(string='Account Report Print PDF Footer Layout', default='l10n_vn_viin.accounting_external_footer_layout')
