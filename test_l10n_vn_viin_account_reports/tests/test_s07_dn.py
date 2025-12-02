import xlrd
from datetime import date, datetime
from odoo.tests import Form
from odoo.tests.common import tagged
from .common import AccountReportL10nVn


@tagged('post_install', '-at_install', 'post_install_l10n')
class TestS07Dn(AccountReportL10nVn):

    def setUp(self):
        super(TestS07Dn, self).setUp()
        journal_items_1 = [{
            'account_id': self.default_account_1112.id,
            'debit': 100000,
            'credit': 0.0
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0.0,
            'credit': 100000
        }]
        self._init_journal_entry(None, datetime.now(), self.default_journal_vn_misc, items=journal_items_1)

    def test_s07_dn(self):
        l10n_vn_viin_s07dn = Form(self.env['l10n_vn.s07dn']).save()
        byte_date = l10n_vn_viin_s07dn.report_excel().getvalue()
        workbook = xlrd.open_workbook(file_contents=byte_date)
        worksheet = workbook.sheet_by_index(0)
        today = date.today().strftime('%m/%d/%Y')
        self.assertEqual(worksheet.cell_value(12, 0), today)
        self.assertEqual(worksheet.cell_value(12, 1), today)
        self.assertEqual(worksheet.cell_value(12, 6), 100000.0)
        self.assertEqual(worksheet.cell_value(12, 7), 0.0)
        self.assertEqual(worksheet.cell_value(12, 8), 100000.0)

        self.assertEqual(worksheet.cell_value(13, 6), 100000.0)
        self.assertEqual(worksheet.cell_value(13, 7), 0.0)
        self.assertEqual(worksheet.cell_value(13, 8), 0.0)

        self.assertEqual(worksheet.cell_value(14, 8), 100000.0)
