from odoo import models, _


class AccountReport(models.Model):
    _inherit = 'account.report'

    def get_circular_code(self):
        # Accountant does not have access right to chart template so add sudo is needed
        return self.chart_template_id.sudo().circular_code or super().get_circular_code()

    def _prepare_wkhtmltopdf_options(self, rcontext):
        opts = super()._prepare_wkhtmltopdf_options(rcontext)
        # we show both header and footer on the entire report if it has a chart template,
        # so we need to add some margin to the report
        if self.chart_template_id:
            opts['specific_paperformat_args'].update({
                'data-report-margin-top': 40,
                'data-report-header-spacing': 35
            })
        return opts

    def _write_xlsx_header(self, sheet, values, x_offset, y_offset):
        super()._write_xlsx_header(sheet, values, x_offset, y_offset)
        # Write template ref
        num_table_col = values['num_table_col']
        template_ref = self.template_ref
        if template_ref:
            template_ref_title_format = values['formats']['template_ref_title_format']
            template_ref_circular_format = values['formats']['template_ref_circular_format']
            if num_table_col >= 5:
                first_col_template_ref = num_table_col + x_offset - 3
                last_col_template_ref = num_table_col + x_offset - 1
            else:
                first_col_template_ref = num_table_col + x_offset - 2
                last_col_template_ref = num_table_col + x_offset + 1
            circular_code = self.get_circular_code()
            sheet.merge_range(0, first_col_template_ref, 0, last_col_template_ref, template_ref,
                              template_ref_title_format)
            if circular_code == 'c200':
                sheet.merge_range(1, first_col_template_ref, 1, last_col_template_ref,
                                  _('(Released Under the Circular No. 200/2014/TT-BTC'),
                                  template_ref_circular_format)
                sheet.merge_range(2, first_col_template_ref, 2, last_col_template_ref,
                                  _('Dated 22/12/2014 by the Ministry of Finance)'),
                                  template_ref_circular_format)
            elif circular_code == 'c133':
                sheet.merge_range(1, first_col_template_ref, 1, last_col_template_ref,
                                  _('(Released Under the Circular No. 133/2016/TT-BTC'),
                                  template_ref_circular_format)
                sheet.merge_range(2, first_col_template_ref, 2, last_col_template_ref,
                                  _('Dated 26/8/2016 by the Ministry of Finance)'),
                                  template_ref_circular_format)
