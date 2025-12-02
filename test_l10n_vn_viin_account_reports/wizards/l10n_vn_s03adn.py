import xlsxwriter
from io import BytesIO
from odoo import models, fields, _
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, format_date


class WizardL10nVnS03adn(models.TransientModel):
    _name = 'l10n_vn.s03adn'
    _inherit = 'account.common.report'
    _description = 'VietNam S03a-DN Report Wizard'

    date_from = fields.Date(default=fields.Date.today().replace(day=1, month=1))
    date_to = fields.Date(default=fields.Date.today)

    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
        ], string='Target Moves')

    def _print_report(self, data):
        res = self.env.ref('l10n_vn_viin_account_reports.report_l10n_vn_s03adn_action').report_action(self, data=data)
        return res

    def check_report_excel(self):
        if self.date_from and self.date_to:
            self._validate_date_from_and_date_to(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/general-journal/download/xlsx/%d' % self.id,
            'target': 'new'
        }

    def report_excel(self):
        self.ensure_one()
        data = self._prepare_check_report()
        return self._export_excel(data)

    def _prepare_check_report(self):
        self.ensure_one()
        data = {}
        # Get data context
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')

        # Format date
        data['form']['date_from'] = data['form']['date_from'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data['form']['used_context']['date_from'] = data['form']['used_context']['date_from'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data['form']['date_to'] = data['form']['date_to'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data['form']['used_context']['date_to'] = data['form']['used_context']['date_to'].strftime(DEFAULT_SERVER_DATE_FORMAT)

        # Get line
        lines = self.env['report.l10n_vn_viin_account_reports.report_s03adn']._get_lines(data)
        dict_data = {
            'data': data,
            'lines': lines,
            'account_ids': False,
            'journal_ids': False,
            'partner_ids': False
            }

        return dict_data

    def _build_contexts(self, data):
        self.ensure_one()
        result = super(WizardL10nVnS03adn, self)._build_contexts(data)
        result['target_type'] = data['form'].get('target_type', False)
        if result['target_type'] == 'account':
            result['account_ids'] = data['form'].get('account_ids', False)
            result['journal_ids'] = False
        else:
            result['account_ids'] = False
        return result

    def _export_excel(self, data):
        ''' Method use create file Excel'''
        self.ensure_one()

        # Create an new Excel file and add a worksheet.
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()

        company = self.company_id
        temp = [company.street, company.street2, company.city, company.state_id.name, company.country_id.name]
        address = ', '.join([index for index in temp if index])

        # Set dimension for column and Format cells:
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(80)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 40)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 20)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 12)
        worksheet.set_column(11, 11, 12)
        worksheet.set_column(12, 12, 20)
        worksheet.set_row(0, 20)
        worksheet.set_row(1, 20)
        worksheet.set_row(2, 20)
        worksheet.set_row(4, 20)
        worksheet.set_row(5, 20)
        worksheet.set_row(7, 25)
        worksheet.set_row(8, 30)
        worksheet.set_row(9, 25)

        # Add a bold format to use to highlight cells.
        title_report_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
            'font_name': 'Times New Roman'
        })
        date_format = workbook.add_format({
            'align': 'center',
            'font_size': 12,
            'text_wrap': True,
            'font_name': 'Times New Roman'
        })
        currency_format = workbook.add_format({
            'align': 'left',
            'font_size': 12,
            'text_wrap': True,
            'font_name': 'Times New Roman'
        })
        name_style_format = workbook.add_format({
            'bold': True,
            'bg_color': '#87CEFA',
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        table_content_style_left_wrap = workbook.add_format({
            'align': 'left',
            'text_wrap': True,
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        table_content_style_right = workbook.add_format({
            'align': 'right',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11,
            'num_format': '#,##0'
        })
        table_content_style_center = workbook.add_format({
            'align': 'center',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        table_content_style_right_two_decimal = workbook.add_format({
            'align': 'right',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12,
            'num_format': '#,##0.00'
        })
        footer_content_center = workbook.add_format({
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        footer_content_center_bold = workbook.add_format({
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 11,
            'bold': True
        })
        content_style_left = workbook.add_format({
            'align': 'left',
            'font_name': 'Times New Roman',
            'font_size': 14
        })
        name_content_tittle_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 14})
        name_content_style = workbook.add_format({
            'align': 'center',
            'font_name': 'Times New Roman',
            'font_size': 14})

        # Header
        worksheet.write('C1', '   ' + _('Company: ') + self.company_id.name, content_style_left)
        worksheet.write('C2', '   ' + _('Address: ') + address, content_style_left)
        worksheet.merge_range('J1:L1', _('Template S03a-DN'), name_content_tittle_style)
        worksheet.merge_range('J2:L2', _('(Released Under the Circular No. 200/2014/TT-BTC'), name_content_style)
        worksheet.merge_range('J3:L3', _('Dated 22/12/2014 by the Ministry of Finance)'), name_content_style)

        #         Add data default into file excel
        date_from = format_date(self.env, data['data']['form']['date_from'])
        date_to = format_date(self.env, data['data']['form']['date_to'])

        worksheet.merge_range('E4:J5', _('GENERAL JOURNAL'), title_report_format)
        worksheet.merge_range('E6:J6', _('Date From: ') + date_from + _(' - Date To: ') + date_to, date_format)
        worksheet.merge_range('F8:G8', _('Currency:'), currency_format)
        worksheet.write('H8', self.company_id.currency_id.name, currency_format)

        #         Header Table
        worksheet.merge_range('A9:A10', _('No.'), name_style_format)
        worksheet.merge_range('B9:B10', _('Date'), name_style_format)
        worksheet.merge_range('C9:D10', _('Origin'), name_style_format)
        worksheet.merge_range('E9:E10', _('Description'), name_style_format)
        worksheet.merge_range('F9:F10', _('Registered'), name_style_format)
        worksheet.merge_range('G9:G10', _('Account'), name_style_format)
        worksheet.merge_range('H9:H10', _('Counterpart \nAccounts'), name_style_format)
        worksheet.merge_range('I9:I10', _('Debit'), name_style_format)
        worksheet.merge_range('J9:J10', _('Credit'), name_style_format)
        worksheet.merge_range('K9:K10', _('Amount \n Currency'), name_style_format)
        worksheet.merge_range('L9:L10', _('Exchange \n Rate'), name_style_format)
        worksheet.merge_range('M9:M10', _('Partner'), name_style_format)

        worksheet.write('C10', _('Origin No.'), name_style_format)
        worksheet.write('D10', _('Origin Date'), name_style_format)

        worksheet.write('A11', _('1'), name_style_format)
        worksheet.write('B11', _('2'), name_style_format)
        worksheet.write('C11', _('3'), name_style_format)
        worksheet.write('D11', _('4'), name_style_format)
        worksheet.write('E11', _('5'), name_style_format)
        worksheet.write('F11', _('6'), name_style_format)
        worksheet.write('G11', _('7'), name_style_format)
        worksheet.write('H11', _('8'), name_style_format)
        worksheet.write('I11', _('9'), name_style_format)
        worksheet.write('J11', _('10'), name_style_format)
        worksheet.write('K11', _('11'), name_style_format)
        worksheet.write('L11', _('12'), name_style_format)
        worksheet.write('M11', _('13'), name_style_format)

        # create lines
        row = 12
        line_no = 0
        for line in data['lines']:
            worksheet.set_row(row - 1, 25)
            table_content_style_right_currency = workbook.add_format({
                                           'align': 'right',
                                           'border': 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 11,
                                           'num_format': '#,##0'
                                           })
            table_content_style_right_amount_currency = workbook.add_format({
                                           'align': 'right',
                                           'border': 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 11,
                                            'num_format': '#,##0.00 [$%s];-#,##0.00 [$%s]' % (line.get('symbol_amount_currency'), line.get('symbol_amount_currency'))
                                           })
            line_no = line_no + 1
            worksheet.write('A%s' % row, line_no, table_content_style_right)
            if line['state'] == 'posted':
                worksheet.write('B%s' % row, format_date(self.env, line['date']), table_content_style_left_wrap)
                worksheet.write('F%s' % row, 'X', table_content_style_center)
            else:
                worksheet.write('B%s' % row, '', table_content_style_left_wrap)
                worksheet.write('F%s' % row, '', table_content_style_center)

            worksheet.write('C%s' % row, line['move_name'], table_content_style_left_wrap)
            worksheet.write('D%s' % row, format_date(self.env, line['move_date']), table_content_style_left_wrap)
            worksheet.write('E%s' % row, line['lname'], table_content_style_left_wrap)
            worksheet.write('G%s' % row, line['account_code'], table_content_style_right)
            worksheet.write('H%s' % row, line['counterpart'], table_content_style_right)
            worksheet.write('I%s' % row, line['debit'], table_content_style_right_currency)
            worksheet.write('J%s' % row, line['credit'], table_content_style_right_currency)
            if line['amount_currency']:
                worksheet.write('K%s' % row, line['amount_currency'], table_content_style_right_amount_currency)
            else:
                worksheet.write('K%s' % row, line['amount_currency'], table_content_style_right)
            if line['exchange_rate'] != 1:
                worksheet.write('L%s' % row, line['exchange_rate'], table_content_style_right_two_decimal)
            else:
                worksheet.write('L%s' % row, line['exchange_rate'], table_content_style_right)

            worksheet.write('M%s' % row, line['partner'], table_content_style_left_wrap)

            row = row + 1

        # Footer
        worksheet.merge_range('B{0}:D{0}'.format(row + 3), _('Prepared By'), footer_content_center_bold)
        worksheet.merge_range('B{0}:D{0}'.format(row + 4), _('(Signature, Full Name)'), footer_content_center)

        worksheet.merge_range('F{0}:H{0}'.format(row + 3), _('Chief Accountant'), footer_content_center_bold)
        worksheet.merge_range('F{0}:H{0}'.format(row + 4), _('(Signature, Full Name)'), footer_content_center)

        worksheet.merge_range('J{0}:L{0}'.format(row + 2), _('Month ..... Day ..... Year .....'), footer_content_center)
        worksheet.merge_range('J{0}:L{0}'.format(row + 3), _('Director/CEO'), footer_content_center_bold)
        worksheet.merge_range('K{0}:M{0}'.format(row + 4), _('(Signature, Full Name, Job Title)'), footer_content_center)

        workbook.close()
        # Back cusor the beginning of the file
        file_data.seek(0)
        return file_data
