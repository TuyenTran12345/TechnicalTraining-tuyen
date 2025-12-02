import xlsxwriter
from io import BytesIO
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.account.models.company import MONTH_SELECTION


class AbstractL10nVnC119Wizard(models.AbstractModel):
    _name = 'abstract.l10n_vn.c119.gtgt'
    _description = 'Invoice Declaration Abstract'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    type = fields.Selection([('month', 'Month'), ('quarter', 'Quarter')], string='Types', required=True, default='month')
    month = fields.Selection(MONTH_SELECTION, string='Month', default='1')
    quarter = fields.Selection([('I', 'Quarter I'), ('II', 'Quarter II'), ('III', 'Quarter III'), ('IV', 'Quarter IV')], string='Quarter', default='I')

    def _get_domain(self):
        raise ValidationError(_("The method '_get_domain' has NOT been implemented."))

    def _add_content_body(self, moves, content_body):
        raise ValidationError(_("The method '_add_content_body' has NOT been implemented."))

    def _get_data(self):
        """Method use get data export to Excel"""
        content_body = {}
        domain = self._get_domain()
        moves = self.env['account.move'].search(domain)
        content_body = self._add_content_body(moves, content_body)
        return content_body

    def _create_file_worksheet(self):
        """ Create an new Excel file, add a worksheet and define type format cell
        :return: file data, workbook, worksheet and type format cell"""
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(80)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 45)
        worksheet.set_column(4, 4, 25)
        worksheet.set_column(5, 5, 25)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 30)
        worksheet.set_row(0, 35)
        worksheet.set_row(1, 35)
        worksheet.set_row(2, 45)
        worksheet.set_row(5, 25)
        worksheet.set_row(6, 25)
        worksheet.set_row(7, 25)
        # Add a bold format to use to highlight cells
        title_report_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
            'font_name': 'Times New Roman'
        })
        title_template = workbook.add_format({
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_name': 'Times New Roman'
        })
        interval_format = workbook.add_format({
            'border': 1,
            'font_size': 12,
            'text_wrap': True,
            'font_name': 'Times New Roman'})
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
        content_cell_format_center = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman'
        })
        content_cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 12,
            'font_name': 'Times New Roman'
        })
        content_cell_format_values = workbook.add_format({
            'border': 1,
            'font_size': 12,
            'font_name': 'Times New Roman',
            'num_format': '#,##0'
        })
        content_cell_format_total = workbook.add_format({
            'bold': True,
            'border': 1,
            'font_size': 12,
            'font_name': 'Times New Roman',
            'num_format': '#,##0'
        })
        content_cell_format_title = workbook.add_format({
            'bold': True,
            'border': 1,
            'font_size': 12,
            'font_name': 'Times New Roman'
        })
        name_style_format_footer = workbook.add_format({
            'align': 'center',
            'font_size': 12,
            'font_name': 'Times New Roman'
        })
        name_style_format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font_name': 'Times New Roman'
        })
        return file_data, workbook, worksheet, \
             title_report_format, title_template, interval_format, \
             date_format, currency_format, name_style_format, \
             content_cell_format_center, content_cell_format, content_cell_format_values, \
             content_cell_format_total, content_cell_format_title, name_style_format_footer, \
             name_style_format_title

    @api.onchange('type', 'month', 'quarter')
    def _onchange_type(self):
        if self.type == 'month':
            self.date_from = self.month and fields.Date.today().replace(day=1, month=int(self.month)) or False
            self.date_to = self.month and self.date_from + relativedelta(day=1, months=+1, days=-1) or False
        elif self.type == 'quarter':
            if self.quarter == 'I':
                self.date_from = fields.Date.today().replace(day=1, month=1)
                self.date_to = fields.Date.today().replace(day=31, month=3)
            elif self.quarter == 'II':
                self.date_from = fields.Date.today().replace(day=1, month=4)
                self.date_to = fields.Date.today().replace(day=30, month=6)
            elif self.quarter == 'III':
                self.date_from = fields.Date.today().replace(day=1, month=7)
                self.date_to = fields.Date.today().replace(day=30, month=9)
            elif self.quarter == 'IV':
                self.date_from = fields.Date.today().replace(day=1, month=10)
                self.date_to = fields.Date.today().replace(day=31, month=12)
            else:
                self.date_from = self.date_to = False

    @api.model
    def _validate_date_from_and_date_to(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("The Date From cannot be greater than the Date To"))
        return True

    def _dispatch_move_lines(self, moves):
        base_lines = moves.line_ids\
            .filtered(lambda x: any(tax.is_vat for tax in x.tax_ids) and not x.tax_line_id)\
            .sorted(lambda x: (x.move_id.id, x.id, -abs(x.amount_currency)))
        tax_lines = moves.line_ids\
            .filtered('tax_line_id.is_vat')\
            .sorted(lambda x: (x.move_id.id, x.tax_line_id.id, x.tax_ids.ids, x.tax_repartition_line_id.id))
        return base_lines, tax_lines
