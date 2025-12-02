import xlrd

from datetime import date
from odoo.tests import Form, tagged
from odoo.exceptions import UserError

from .common import AccountReportL10nVn


@tagged('post_install', '-at_install', 'post_install_l10n')
class Test02GTGT(AccountReportL10nVn):

    def setUp(self):
        super(Test02GTGT, self).setUp()

    def test_02_gtgt(self):
        now = date.today()

        # Case 1: Type is Month
        c119_02_gtgt_form = Form(self.env['l10n_vn.c119.02gtgt'])
        c119_02_gtgt_form.type = 'month'
        c119_02_gtgt_form.month = '9'
        self.assertEqual(c119_02_gtgt_form.date_from, date(now.year, 9, 1))
        self.assertEqual(c119_02_gtgt_form.date_to, date(now.year, 9, 30))

        # Case 2: Type is Quarter
        c119_02_gtgt_form.type = 'quarter'
        c119_02_gtgt_form.quarter = 'III'
        self.assertEqual(c119_02_gtgt_form.date_from, date(now.year, 7, 1))
        self.assertEqual(c119_02_gtgt_form.date_to, date(now.year, 9, 30))

        # Case 3: Date From is smaller than Date To
        c119_02_gtgt_form.date_to = date(now.year, 6, 30)
        c119_02_gtgt = c119_02_gtgt_form.save()
        with self.assertRaises(UserError):
            c119_02_gtgt.print_purchase()

        # Case 4: Export file excel
        invoice_date = date(now.year, 8, 1)
        invoice = self.init_invoice("out_invoice", self.customer_a, invoice_date, post=False, amounts=[10000], taxes=[])
        invoice.invoice_line_ids[0].analytic_tag_ids = [(4, self.env.ref('viin_analytic_tag.account_analytic_tag_vat_taxable').id)]
        invoice.action_post()

        c119_02_gtgt.date_to = date(now.year, 9, 30)
        byte_date = c119_02_gtgt.export_excel_purchase().getvalue()
        workbook = xlrd.open_workbook(file_contents=byte_date)
        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.cell_value(3, 3), "Date from: 07/01/%s - Date to: 09/30/%s" % (now.year, now.year))
