from collections import defaultdict
from operator import itemgetter

from odoo import api, models, _
from odoo.tools.misc import format_date
from odoo.tools import groupby


class WizardL10nVn11902GTGT (models.TransientModel):
    _name = 'l10n_vn.c119.02gtgt'
    _inherit = 'abstract.l10n_vn.c119.gtgt'
    _description = 'Vietnam Invoice Declaration purchase 01 -2/GTGT'

    def _get_domain(self):
        """Method use get domain"""
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                  ('move_type', 'in', ('in_invoice', 'in_refund')), ('state', '=', 'posted'),
                  ('company_id', 'in', self.company_id.ids)]
        return domain

    def _add_content_body(self, moves, content_body):
        tags = self.env['account.analytic.tag'].concat(*self._get_purchase_tag_vat())
        default_tag = self.env.ref('viin_analytic_tag.account_analytic_tag_vat_vat_taxable_and_exemption')
        full_base_lines, tax_lines = self._dispatch_move_lines(moves)
        base_line_ids, tax_content_body = self._get_purchase_tax_details(tax_lines)
        lines_unmatched = full_base_lines - self.env['account.move.line'].browse(base_line_ids).exists()

        content_body.update({tag.id: [] for tag in tags})

        for tag_id, tax_line_vals in tax_content_body.items():
            vals = self._get_purchase_tax_details_content(tax_line_vals)
            if vals:
                content_body[tag_id].extend(vals)

        if lines_unmatched:
            query = self.env['account.move.line']._where_calc([('id', 'in', lines_unmatched.ids)])
            from_clause, where_clause, where_clause_params = query.get_sql()
            self.env['account.move.line'].flush_model()
            sql = """
                SELECT
                    account_move_line.id AS base_line_id,
                    account_move_line.balance AS base_amount,
                    0 AS tax_amount
                FROM %(from)s
                WHERE %(where)s
            """ % {'from': from_clause, 'where': where_clause}
            self.env.cr.execute(sql, where_clause_params)
            tax_details_res = self.env.cr.dictfetchall()
            for tax_vals in tax_details_res:
                vals = self._get_purchase_tax_details_content([tax_vals])
                base_line = self.env['account.move.line'].browse(tax_vals['base_line_id'])
                if analytic_tag := list(set(base_line.analytic_tag_ids) & set(tags)):
                    content_body[analytic_tag[0].id].extend(vals)
                else:
                    content_body[default_tag.id].extend(vals)

        content_body = {key: sorted(value, key=itemgetter(1)) for key, value in content_body.items()}

        return content_body

    @api.model
    def _get_purchase_tag_vat(self):
        return [
            self.env.ref('viin_analytic_tag.account_analytic_tag_vat_taxable', raise_if_not_found=False),
            self.env.ref('viin_analytic_tag.account_analytic_tag_vat_exemption', raise_if_not_found=False),
            self.env.ref('viin_analytic_tag.account_analytic_tag_vat_vat_taxable_and_exemption', raise_if_not_found=False),
            self.env.ref('viin_analytic_tag.account_analytic_tag_goods_and_services_investment_projects', raise_if_not_found=False)
        ]

    def _get_purchase_tax_details(self, tax_move_lines):
        purchase_tax_details = defaultdict(list)
        base_line_id = set()
        if not tax_move_lines:
            return base_line_id, purchase_tax_details

        tax_details_query, tax_details_params = self.env['account.move.line']._get_query_tax_details_from_domain(domain=[('id', 'in', tax_move_lines.ids)])
        self.env['account.move.line'].flush_model()
        self.env.cr.execute(f"""
            SELECT
                tax_details.base_line_id,
                tax_details.base_account_id,
                tax_details.tax_repartition_line_id,
                MIN(tax_details.base_amount) AS base_amount,
                SUM(tax_details.tax_amount) AS tax_amount
            FROM ({tax_details_query}) AS tax_details
            GROUP BY tax_details.base_line_id, tax_details.base_account_id, tax_details.tax_repartition_line_id
        """, tax_details_params)
        tax_details_res = self.env.cr.dictfetchall()
        tags = self.env['account.analytic.tag'].concat(*self._get_purchase_tag_vat())

        default_tag = self.env.ref('viin_analytic_tag.account_analytic_tag_vat_vat_taxable_and_exemption')
        for tax_vals in tax_details_res:
            base_line = self.env['account.move.line'].browse(tax_vals['base_line_id'])
            if analytic_tag := list(set(base_line.analytic_tag_ids) & set(tags)):
                base_line_id.add(tax_vals['base_line_id'])
                purchase_tax_details[analytic_tag[0].id].append(tax_vals)
            else:
                base_line_id.add(tax_vals['base_line_id'])
                purchase_tax_details[default_tag.id].append(tax_vals)

        return base_line_id, purchase_tax_details

    def _get_purchase_tax_details_content(self, tax_line_vals):
        if not tax_line_vals:
            return

        result = []
        for base_move, tax_lines in groupby(tax_line_vals, key=lambda res: self.env['account.move.line'].browse(res['base_line_id']).move_id):
            sign = 1 if base_move.is_outbound() else -1
            vals = (
                # TODO: master/17+, remove `move.legal_number` as it is here for compatibility
                # see https://github.com/Viindoo/tvtmaaddons/pull/11686
                base_move.ref or base_move.legal_number or base_move.name or '',
                base_move.invoice_date or base_move.date,
                base_move.partner_id.commercial_partner_id.name or '',
                base_move.partner_id.commercial_partner_id.vat or '',
                sign * abs(sum([tax_line['base_amount'] for tax_line in tax_lines])),
                sign * abs(sum([tax_line['tax_amount'] for tax_line in tax_lines])),
            )
            result.append(vals)
        return result

    def export_excel_purchase(self):
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
        title_rule = _('Template: 01 -2/GTGT (Released Under the Circular No. 119/2014/TT-BTC Dated 22/12/2014 by the Ministry of Finance)')
        worksheet.merge_range('G1:H2', title_rule, title_template)
        worksheet.merge_range('D3:F3', _('LIST OF INVOICES, FINANCIAL PAPERS OF PURCHASED GOODS AND SERVICES'), title_report_format)
        worksheet.merge_range('D4:F4', _('Date from: %s - Date to: %s') % (date_from, date_to), date_format)
        worksheet.write('G5', _('Currency:'), currency_format)
        worksheet.write('H5', self.company_id.currency_id.name, currency_format)
        # Header_title
        worksheet.merge_range('A6:A7', _('No'), name_style_format)
        worksheet.merge_range('B6:C6', _('Invoice, Bill'), name_style_format)
        worksheet.merge_range('D6:D7', _('Vendor'), name_style_format)
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
            tag = self.env['account.analytic.tag'].browse(key).exists()
            sequence = 1
            total_tax = 0
            total = 0
            worksheet.set_row(sequence_vat + count + 8, 20)
            if tag == self.env.ref('viin_analytic_tag.account_analytic_tag_vat_taxable'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Taxable Goods & Services for Production and Business be eligible for VAT deduction') % (sequence_vat,),
                    content_cell_format_title
                    )
            elif tag == self.env.ref('viin_analytic_tag.account_analytic_tag_vat_exemption'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Exemption Goods & Services for Production and Business') % (sequence_vat,),
                    content_cell_format_title
                    )
            elif tag == self.env.ref('viin_analytic_tag.account_analytic_tag_vat_vat_taxable_and_exemption'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Taxable and Exemption Goods & Services for Production and Business be eligible for VAT deduction') % (sequence_vat,),
                    content_cell_format_title
                    )
            elif tag == self.env.ref('viin_analytic_tag.account_analytic_tag_goods_and_services_investment_projects'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. Goods & Services for Investment Projects be eligible for VAT deduction') % (sequence_vat,),
                    content_cell_format_title
                    )
            for row in values:
                worksheet.set_row(sequence_vat + count + 8, 20)
                worksheet.write(sequence_vat + count + 8, 0, sequence, content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 1, row[0], content_cell_format)
                worksheet.write(sequence_vat + count + 8, 2, format_date(self.env, row[1]), content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 3, row[2], content_cell_format)
                worksheet.write(sequence_vat + count + 8, 4, row[3], content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 5, row[4], content_cell_format_values)
                worksheet.write(sequence_vat + count + 8, 6, row[5], content_cell_format_values)
                worksheet.write(sequence_vat + count + 8, 7, " ", content_cell_format)
                sequence += 1
                total += row[4]
                total_tax += row[5]
                count += 1
            count += 1
            sequence_vat += 1
            taxes_total += total_tax
            untaxed_total += total
            worksheet.merge_range('A{0}:E{0}'.format(sequence_vat + count + 7), _('Total'), content_cell_format_title)
            if tag == self.env.ref('viin_analytic_tag.account_analytic_tag_vat_exemption'):
                worksheet.write_comment('G{0}'.format(sequence_vat + count + 7), _('is a summary of non-deductible tax'))
            worksheet.write(sequence_vat + count + 6, 5, total, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 6, total_tax, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 7, " ", interval_format)

        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 9), _('Untaxed Amount Total (Purchase)'), content_cell_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 9), untaxed_total, content_cell_format_total)
        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 10), _('Taxes Total (Purchase)'), content_cell_format_title)
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

    def print_purchase(self):
        self._validate_date_from_and_date_to(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/invoice-declaration-purchase/download/xlsx/%d' % self.id,
            'target': 'new'
        }
