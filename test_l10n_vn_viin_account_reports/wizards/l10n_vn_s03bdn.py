from io import BytesIO
import xlsxwriter
from odoo import models, fields, _
from odoo.tools.misc import format_date


class WizardL10nVnS03bdn(models.TransientModel):
    _name = 'l10n_vn.s03bdn'
    _inherit = 'l10n_vn.s38dn'
    _description = 'VietNam S03b-DN Report Wizard'

    target_type = fields.Selection(default='account')

    def _print_report(self, data):
        res = self.env.ref('l10n_vn_viin_account_reports.report_l10n_vn_s03bdn_action').report_action(self, data=data)
        return res

    def check_report_excel(self):
        self._validate_date_from_and_date_to(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/ledger/download/xlsx/%d' % self.id,
            'target': 'new'
        }

    def _export_excel(self, data):
        self.ensure_one()

        # get data
        include_extra_info = data['form'].get('include_extra_info', False)
        data = self._data_report_excel(data)

        company = self.company_id
        temp = [company.street, company.street2, company.city, company.state_id.name, company.country_id.name]
        address = ', '.join([index for index in temp if index])

        # Create an new Excel file and add a worksheet.
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(90)
        worksheet.set_default_row(25)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 35)
        worksheet.set_column(5, 5, 25)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 20)
        worksheet.set_column(9, 9, 20)
        if include_extra_info:
            worksheet.set_column(10, 10, 20)
            worksheet.set_column(11, 11, 20)
        worksheet.set_row(5, 35)
        worksheet.set_row(12, 35)

        name_table_style_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'bottom': 2,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 16
        })
        name_content_tittle_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 14
        })
        name_content_style = workbook.add_format({
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 14
        })
        content_style_left = workbook.add_format({
            'align': 'left',
            'font_name': 'Times New Roman',
            'font_size': 14
        })
        content_style_right = workbook.add_format({
            'align': 'right',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 14,
            'num_format': '#,##0'
        })
        name_tittle_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 17
        })
        table_content_left_bold = workbook.add_format({
            'bold': True,
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 14
        })
        table_content_style_left = workbook.add_format({
            'align': 'left',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 14
        })
        table_content_style_center = workbook.add_format({
            'align': 'center',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 14
        })

        space = '   '
        # Header
        worksheet.write('B3', space + _('Company: ') + self.company_id.name, content_style_left)
        worksheet.write('B4', space + _('Address: ') + address, content_style_left)
        worksheet.merge_range(
            'H3:J3' if include_extra_info else 'F3:H3',
            _('Template S03b-DN'),
            name_content_tittle_style
        )
        worksheet.merge_range(
            'H4:J4' if include_extra_info else 'F4:H4',
            _('(Released Under the Circular No. 200/2014/TT-BTC'),
            name_content_style
        )
        worksheet.merge_range(
            'H5:J5' if include_extra_info else 'F5:H5',
            _('Dated 22/12/2014 by the Ministry of Finance)'),
            name_content_style
        )

        worksheet.merge_range(
            'E7:G7' if include_extra_info else 'D7:F7',
            _('LEDGER'),
            name_tittle_style
        )
        worksheet.merge_range(
            'E8:G8' if include_extra_info else 'D8:F8',
            _('(Used for general journal accounting)'),
            name_content_style
        )
        worksheet.merge_range(
            'E9:G9' if include_extra_info else 'D9:F9',
            (
                _('Date From: ') + format_date(self.env, data['data']['form']['date_from']) +
                _('- Date To: ') + format_date(self.env, data['data']['form']['date_to'])
            ),
            name_content_style
        )
        if data['account_ids']:
            worksheet.merge_range(
                'E10:G10' if include_extra_info else 'D10:F10',
                _('Accounts: ') + str(data['account_ids']),
                name_content_style
            )
        worksheet.merge_range(
            'E11:G11' if include_extra_info else 'D11:F11',
            _('Currency: ') + self.company_id.currency_id.name,
            name_content_style
        )

        # Table - Add Column
        worksheet.merge_range('B12:B13', _('Date'), name_table_style_format)
        worksheet.write('B14', 'A', name_table_style_format)

        worksheet.merge_range('C12:D12', _('Origin'), name_table_style_format)
        worksheet.write('C13', _('Reference'), name_table_style_format)
        worksheet.write('D13', _('Ref Date'), name_table_style_format)
        worksheet.write('C14', 'B', name_table_style_format)
        worksheet.write('D14', 'C', name_table_style_format)

        worksheet.merge_range('E12:E13', _('Description'), name_table_style_format)
        worksheet.write('E14', 'D', name_table_style_format)

        worksheet.merge_range('F12:F13', _('Counterpart Accounts'), name_table_style_format)
        worksheet.write('F14', 'E', name_table_style_format)

        worksheet.merge_range('G12:H12', _('Amount'), name_table_style_format)
        worksheet.write('G13', _('Debit'), name_table_style_format)
        worksheet.write('G14', '1', name_table_style_format)
        worksheet.write('H13', _('Credit'), name_table_style_format)
        worksheet.write('H14', '2', name_table_style_format)

        if include_extra_info:
            worksheet.merge_range('I12:J12', _('Extra Info'), name_table_style_format)
            worksheet.write('I13', _('Reference No.'), name_table_style_format)
            worksheet.write('I14', 'F', name_table_style_format)
            worksheet.write('J13', _('Indirect Counterpart \n Accounts'), name_table_style_format)
            worksheet.write('J14', 'G', name_table_style_format)

        # create lines
        row = 15
        for line in data['lines']:
            if line['type'] == 'account_title':
                worksheet.set_row(row - 1, 33)
                worksheet.merge_range(
                    ('B{0}:J{0}' if include_extra_info else 'B{0}:H{0}').format(row),
                    space + line['account_name'],
                    table_content_left_bold
                )
            else:
                name = line['name']
                if name is None:
                    name = ''
                worksheet.write('E%s' % row, space + name, table_content_style_left)
                if line['type'] == 'move_line':
                    worksheet.write('B%s' % row, format_date(self.env, line['date']), table_content_style_center)
                    worksheet.write('C%s' % row, space + line['ref_name'], table_content_style_left)
                    worksheet.write('D%s' % row, format_date(self.env, line['date']), table_content_style_center)
                    worksheet.write('F%s' % row, space + line['account_id'], table_content_style_left)
                    worksheet.write('G%s' % row, line['debit'], content_style_right)
                    worksheet.write('H%s' % row, line['credit'], content_style_right)
                    if include_extra_info:
                        worksheet.write(
                            'I%s' % row,
                            space + (line['ref_indirect_ctp_aml'] and line['ref_indirect_ctp_aml'].replace('<br/>', '\n') or ''),
                            table_content_style_left
                        )
                        worksheet.write('J%s' % row, space + line['indirect_ctp_account_id'], table_content_style_left)
                else:
                    worksheet.merge_range('B{0}:D{0}'.format(row), '', table_content_style_left)
                    if line['type'] == 'account_total':
                        worksheet.write('G%s' % row, line['debit'], content_style_right)
                        worksheet.write('H%s' % row, line['credit'], content_style_right)
                    else:
                        if line['progress'] >= 0:
                            worksheet.write('G%s' % row, line['progress'], content_style_right)
                            worksheet.write('H%s' % row, 0, content_style_right)
                        else:
                            worksheet.write('G%s' % row, 0, content_style_right)
                            worksheet.write('H%s' % row, -line['progress'], content_style_right)
                        worksheet.write('F%s' % row, '', table_content_style_left)
                    if include_extra_info:
                        worksheet.write('I%s' % row, ' ', table_content_style_left)
                        worksheet.write('J%s' % row, ' ', table_content_style_left)
            row += 1

        # Footer
        worksheet.write('B%s' % (row + 1), space + _('- This report has ... pages, from page 01 to page ...'), content_style_left)
        worksheet.write('B%s' % (row + 2), space + _('- Issue Date: ') + format_date(self.env, data['today']), content_style_left)

        worksheet.merge_range('B{0}:C{0}'.format(row + 4), _('Prepared By'), name_content_tittle_style)
        worksheet.merge_range('B{0}:C{0}'.format(row + 5), _('(Signature, Full Name)'), name_content_style)

        worksheet.merge_range(
            ('E{0}:F{0}' if include_extra_info else 'D{0}:E{0}').format(row + 4),
            _('Chief Accountant'),
            name_content_tittle_style
        )
        worksheet.merge_range(
            ('E{0}:F{0}' if include_extra_info else 'D{0}:E{0}').format(row + 5),
            _('(Signature, Full Name)'),
            name_content_style
        )

        worksheet.merge_range(
            ('H{0}:J{0}' if include_extra_info else 'F{0}:H{0}').format(row + 3),
            space + _('Month ..... Day ..... Year .....'),
            name_content_style
        )

        worksheet.merge_range(
            ('H{0}:J{0}' if include_extra_info else 'F{0}:H{0}').format(row + 4),
            _('Director/CEO'),
            name_content_tittle_style
        )
        worksheet.merge_range(
            ('H{0}:J{0}' if include_extra_info else 'F{0}:H{0}').format(row + 5),
            _('(Signature, Full Name, Job Title)'),
            name_content_style
        )

        workbook.close()
        file_data.seek(0)
        return file_data
