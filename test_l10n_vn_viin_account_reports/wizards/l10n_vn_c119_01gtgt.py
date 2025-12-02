from odoo import models, _
from odoo.tools.misc import format_date
from odoo.tools import groupby


class WizardL10nVn11901GTGT (models.TransientModel):
    _name = 'l10n_vn.c119.01gtgt'
    _inherit = 'abstract.l10n_vn.c119.gtgt'
    _description = 'Vietnam Invoice Declaration sale 01 -1/GTGT'

    def _get_domain(self):
        """Method use get domain"""
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                  ('move_type', 'in', ('out_invoice', 'out_refund')), ('state', '=', 'posted'),
                  ('company_id', 'in', self.company_id.ids)]
        return domain

    def _add_content_body(self, moves, content_body):
        Tax = self.env['account.tax']
        tax_sale_vat_exemption_xml_id = 'l10n_vn_viin.%s_account_tax_template_sale_vat_exemption' % self.company_id.id
        tax_sale_vat_exemption = self.env.ref(tax_sale_vat_exemption_xml_id, raise_if_not_found=False) or Tax
        taxes = tax_sale_vat_exemption | Tax.search([('is_vat', '=', True), ('type_tax_use', '=', 'sale'), ('company_id', '=', self.company_id.id)]).sorted(key='amount')

        base_lines, tax_lines = self._dispatch_move_lines(moves)
        tax_details_query, tax_details_params = self.env['account.move.line']._get_query_tax_details_from_domain(domain=[('id', 'in', tax_lines.ids)])

        content_body = {tax.id: [] for tax in taxes}
        MoveLine = self.env['account.move.line']

        self.env['account.move.line'].flush_model()
        self.env.cr.execute(tax_details_query, tax_details_params)
        tax_details_res = self.env.cr.dictfetchall()

        base_tax_matching = MoveLine.browse([e['base_line_id'] for e in tax_details_res])

        tax_details_res.extend([{
            'id': line.id,
            'base_line_id': line.id,
            'tax_line_id': None,
            'display_type': 'tax',
            'src_line_id': line.id,
            'tax_id': line.tax_ids[0].id,
            'group_tax_id': None,
            'tax_exigible': True,
            'base_account_id': line.account_id.id,
            'tax_repartition_line_id': None,
            'base_amount': line.balance,
            'tax_amount': 0.0,
            'base_amount_currency': line.amount_currency,
            'tax_amount_currency': 0.0
        } for line in base_lines - base_tax_matching])

        tax_details_res = sorted(tax_details_res, key=lambda res: MoveLine.browse(res['base_line_id']).date)
        for (tax_id, base_move), tax_lines in groupby(tax_details_res, key=lambda res: (res['tax_id'], MoveLine.browse(res['base_line_id']).move_id)):
            if tax_id in taxes.ids:
                sign = 1 if base_move.is_inbound() else -1
                vals = (
                    base_move.legal_number or base_move.name,
                    base_move.invoice_date,
                    base_move.partner_id.commercial_partner_id.name,
                    base_move.partner_id.commercial_partner_id.vat or '',
                    sign * abs(sum([tax_line['base_amount'] for tax_line in tax_lines])),
                    sign * abs(sum([tax_line['tax_amount'] for tax_line in tax_lines])),
                )
                content_body[tax_id].append(vals)

        return content_body

    def export_excel_sale(self):
        """Method Create file Excel"""
        self.ensure_one()
        # Get data
        content_body = self._get_data()
        company = self.company_id
        temp = [company.street, company.street2, company.city, company.state_id.name, company.country_id.name]
        address = ', '.join([index for index in temp if index])
        # Create an new Excel file and add a worksheet and a bold format to use to highlight cells.
        file_data, workbook, worksheet, \
        title_report_format, title_template, interval_format, \
        date_format, currency_format, name_style_format, \
        content_cell_format_center, content_cell_format, content_cell_format_values, \
        content_cell_format_total, content_cell_format_title, name_style_format_footer, \
        name_style_format_title = self._create_file_worksheet()
        content_style_left = workbook.add_format({
            'align': 'left',
            'font_name': 'Times New Roman',
            'font_size': 14
        })

        # Add data default into file excel
        date_from = format_date(self.env, self.date_from)
        date_to = format_date(self.env, self.date_to)

        # Header
        worksheet.write('A1', '   ' + _('Company: ') + self.company_id.name, content_style_left)
        worksheet.write('A2', '   ' + _('Address: ') + address, content_style_left)
        title_rule = _('Template: 01 -1/GTGT (Released Under the Circular No. 119/2014/TT-BTC Dated 22/12/2014 by the Ministry of Finance)')
        worksheet.merge_range('G1:H2', title_rule, title_template)
        worksheet.merge_range('D3:F3', _('LIST OF INVOICES, FINANCIAL PAPERS OF SOLD GOODS'), title_report_format)
        worksheet.merge_range('D4:F4', _('Date from: %s - Date to: %s') % (date_from, date_to), date_format)
        worksheet.write('G5', _('Currency:'), currency_format)
        worksheet.write('H5', self.company_id.currency_id.name, currency_format)
        # Header_title
        worksheet.merge_range('A6:A7', _('No'), name_style_format)
        worksheet.merge_range('B6:C6', _('Invoice, Bill'), name_style_format)
        worksheet.merge_range('D6:D7', _('Customer'), name_style_format)
        worksheet.merge_range('E6:E7', _('Tax Id'), name_style_format)
        worksheet.merge_range('F6:F7', _('Untaxed Amount'), name_style_format)
        worksheet.merge_range('G6:G7', _('Taxes'), name_style_format)
        worksheet.merge_range('H6:H7', _('Note'), name_style_format)

        worksheet.write('B7', _('Invoice No'), name_style_format)
        worksheet.write('C7', _('Date'), name_style_format)

        worksheet.write('A8', _('1'), name_style_format)
        worksheet.write('B8', _('2'), name_style_format)
        worksheet.write('C8', _('3'), name_style_format)
        worksheet.write('D8', _('4'), name_style_format)
        worksheet.write('E8', _('5'), name_style_format)
        worksheet.write('F8', _('6'), name_style_format)
        worksheet.write('G8', _('7'), name_style_format)
        worksheet.write('H8', _('8'), name_style_format)

        # Insert values into cell content body
        count = 0
        sequence_vat = 1
        untaxed_total = 0
        taxes_total = 0
        for key, values in content_body.items():
            total = 0
            total_tax = 0
            worksheet.set_row(sequence_vat + count + 8, 20)
            tax_sale_vat_exemption_xml_id = 'l10n_vn_viin.%s_account_tax_template_sale_vat_exemption' % self.company_id.id
            account_tax = self.env.ref(tax_sale_vat_exemption_xml_id, raise_if_not_found=False)
            if account_tax and key == account_tax.id:
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Exemption Goods & Services') % (sequence_vat,),
                    content_cell_format_title
                    )
            else:
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Taxable Goods & Services %s%s') % (sequence_vat, str(self.env['account.tax'].browse(key).amount), '%'),
                    content_cell_format_title
                    )
            sequence = 1
            for row in values:
                worksheet.set_row(sequence_vat + count + 8, 20)
                worksheet.write(sequence_vat + count + 8, 0, sequence, content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 1, row[0], content_cell_format)
                worksheet.write(sequence_vat + count + 8, 2, format_date(self.env, row[1]), content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 3, row[2], content_cell_format)
                worksheet.write(sequence_vat + count + 8, 4, row[3], content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 5, row[4], content_cell_format_values)
                worksheet.write(sequence_vat + count + 8, 6, row[5], content_cell_format_values)
                worksheet.write(sequence_vat + count + 8, 7, ' ', content_cell_format)
                sequence += 1
                total += row[4]
                total_tax += row[5]
                count += 1
            count += 1
            sequence_vat += 1
            taxes_total += total_tax
            untaxed_total += total
            worksheet.merge_range(
                'A{0}:E{0}'.format(sequence_vat + count + 7),
                _('Total'),
                content_cell_format_title
                )
            worksheet.write(sequence_vat + count + 6, 5, total, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 6, total_tax, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 7, ' ', interval_format)

        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 9), _('Untaxed Amount Total (Sales)'), content_cell_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 9), untaxed_total, content_cell_format_total)
        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 10), _('Taxes Total (Sales)'), content_cell_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 10), taxes_total, content_cell_format_total)

        # Footer
        worksheet.merge_range('A{0}:B{0}'.format(sequence_vat + count + 13), _('Prepared By'), name_style_format_title)
        worksheet.merge_range('A{0}:B{0}'.format(sequence_vat + count + 14), _('(Signature, Full Name)'), name_style_format_footer)

        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 13), _('Chief Accountant'), name_style_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 14), _('(Signature, Full Name)'), name_style_format_footer)

        worksheet.merge_range('F{0}:H{0}'.format(sequence_vat + count + 12), _('Month ..... Day ..... Year .....'), name_style_format_footer)
        worksheet.merge_range('F{0}:H{0}'.format(sequence_vat + count + 13), _('Director/CEO'), name_style_format_title)
        worksheet.merge_range('F{0}:H{0}'.format(sequence_vat + count + 14), _('(Signature, Full Name, Job Title)'), name_style_format_footer)

        workbook.close()
        # Back cursor to the beginning of the file
        file_data.seek(0)
        return file_data

    def print_sale(self):
        self._validate_date_from_and_date_to(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/invoice-declaration-sales/download/xlsx/%d' % self.id,
            'target': 'new'
        }
