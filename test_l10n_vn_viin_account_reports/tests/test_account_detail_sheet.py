import logging
from datetime import date
from odoo.tests.common import tagged, SingleTransactionCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'post_install_l10n')
class TestAccountDetailSheet(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountDetailSheet, cls).setUpClass()

        cls.company_test = cls.env['res.company'].create({
            'name': 'Company Test',
        })
        cls.env.user.company_ids |= cls.company_test
        chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not chart_template_vn:
            _logger.warn("Test skipped because VN Chart template not found ...")
            cls.skipTest(cls, "VN Chart template not found")
        chart_template_vn.with_context(mail_activity_quick_update=True).try_loading(company=cls.company_test)
        # search all accounts and journals of company
        accounts = cls.env['account.account'].search([('company_id', '=', cls.company_test.id)])
        journals = cls.env['account.journal'].search([('company_id', '=', cls.company_test.id)])

        cls.account_131 = accounts.filtered(lambda a: a.code == '131')[:1]
        cls.account_1121 = accounts.filtered(lambda a: a.code == '1121')[:1]
        cls.account_5111 = accounts.filtered(lambda a: a.code == '5111')[:1]
        cls.journal_bank = journals.filtered(lambda j: j.type == 'bank')[:1]
        cls.journal_customer_invoice = journals.filtered(lambda j: j.type == 'sale')[:1]

        context_no_mail = {'mail_create_nosubscribe': True, 'mail_create_nolog': True, 'tracking_disable': True}
        cls.partner_A = cls.env['res.partner'].with_context(context_no_mail).create({
                                                                                    'name': 'Partner A',
                                                                                    'email': 'partnerA@example.viindoo.com',
                                                                                })
        cls.partner_B = cls.env['res.partner'].with_context(context_no_mail).create({
                                                                                    'name': 'Partner B',
                                                                                    'email': 'partnerB@example.viindoo.com',
                                                                                })

        cls.move1 = cls.env['account.move'].with_context(tracking_disable=True).create({
            'journal_id': cls.journal_customer_invoice.id,
            'date': date(2021, 10, 10),
            'line_ids': [(0, 0, {'account_id': cls.account_131.id, 'debit': 500.0, 'credit': 0.0, 'partner_id': cls.partner_A.id}),
                         (0, 0, {'account_id': cls.account_5111.id, 'debit': 0.0, 'credit': 500.0})]
        })
        cls.move1._post()
        cls.move2 = cls.env['account.move'].with_context(tracking_disable=True).create({
            'journal_id': cls.journal_bank.id,
            'date': date(2021, 10, 15),
            'line_ids': [(0, 0, {'account_id': cls.account_1121.id, 'debit': 500.0, 'credit': 0.0, 'partner_id': cls.partner_B.id}),
                         (0, 0, {'account_id': cls.account_131.id, 'debit': 0.0, 'credit': 500.0, 'partner_id': cls.partner_B.id})]
        })
        cls.move2._post()

    @staticmethod
    def _prepare_report_form_data(date_from, date_to, target_move, target_type, journal_ids, account_ids, partner_ids, company_id):
        return {
            'date_from': date_from,
            'date_to': date_to,
            'target_move': target_move,
            'target_type': target_type,
            'journal_ids': [(6, 0, journal_ids)],
            'partner_ids': [(6, 0, partner_ids)],
            'account_ids': [(6, 0, account_ids)],
            'company_id': company_id
        }

    @staticmethod
    def _get_valid_lines_data(lines, keys):
        new_lines = []
        for line in lines:
            new_lines.append({key: line.get(key, False) for key in list(set(line.keys()) & set(keys))})
        return new_lines

    def test_01_moves_state_on_report(self):
        Wizard = self.env['l10n_vn.s38dn']
        # Get only posted entries for report
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'journal',
                                [self.journal_bank.id, self.journal_customer_invoice.id], [], [], self.company_test.id))
        data = wizard1._prepare_check_report()
        lines = wizard1._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                                'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_1121.code, self.account_1121.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 15),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '1121',
                'date': date(2021, 10, 15),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_5111.code, self.account_5111.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 10),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)

    def test_02_period_on_report(self):
        Wizard = self.env['l10n_vn.s38dn']
        # report from 1/10/2021 to 14/10/2021
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 14), 'posted', 'journal',
                                   [self.journal_bank.id, self.journal_customer_invoice.id], [], [], self.company_test.id))
        data = wizard1._prepare_check_report()
        lines = wizard1._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                                 'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0,
                'progress': 500,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_5111.code, self.account_5111.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 10),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)
        # report from 1/10/2021 to 31/10/2021
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'journal',
                                   [self.journal_bank.id, self.journal_customer_invoice.id], [], [], self.company_test.id))
        data = wizard2._prepare_check_report()
        lines = wizard2._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                             'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_1121.code, self.account_1121.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 15),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '1121',
                'date': date(2021, 10, 15),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_5111.code, self.account_5111.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 10),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)

    def test_03_journals_on_report(self):
        Wizard = self.env['l10n_vn.s38dn']
        # Choose Customer Invoice Journal
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'journal',
                                                       [self.journal_customer_invoice.id], [], [], self.company_test.id))
        data = wizard1._prepare_check_report()
        lines = wizard1._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                                 'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0,
                'progress': 500,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_5111.code, self.account_5111.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 10),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)
        # Choose Bank Journal
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'journal',
                                                                [self.journal_bank.id], [], [], self.company_test.id))
        data = wizard2._prepare_check_report()
        lines = wizard2._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                             'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_1121.code, self.account_1121.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 15),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '1121',
                'date': date(2021, 10, 15),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 0.0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 0,
                'progress_credit': 500.0,
                'progress': -500.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)

    def test_04_accounts_on_report(self):
        Wizard = self.env['l10n_vn.s38dn']
        # Choose Target Type: Account, Accounts: 131
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'account',
                                                                [], [self.account_131.id], [], self.company_test.id))
        data = wizard1._prepare_check_report()
        lines = wizard1._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                                 'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '1121',
                'date': date(2021, 10, 15),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)
        # Choose Target Type: Account, Accounts: 131, 1121
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'account',
                                                [], [self.account_131.id, self.account_1121.id], [], self.company_test.id))
        data = wizard2._prepare_check_report()
        lines = wizard2._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                                 'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_1121.code, self.account_1121.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 15),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '1121',
                'date': date(2021, 10, 15),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)

    def test_05_partners_on_report(self):
        Wizard = self.env['l10n_vn.s38dn']
        # Choose Partner: Partner A
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'journal',
                                                                     [], [], [self.partner_A.id], self.company_test.id))
        data = wizard1._prepare_check_report()
        lines = wizard1._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                             'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0,
                'progress': 500.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)
        # Choose Partner: Partner A, Partner B
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', 'journal',
                                                    [], [], [self.partner_A.id, self.partner_B.id], self.company_test.id))
        data = wizard2._prepare_check_report()
        lines = wizard2._data_report_excel(data).get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['type', 'account_name', 'name', 'account_id', 'debit', 'credit',
                                                                 'date', 'progress', 'progress_debit', 'progress_credit'])
        expected_values = [
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_1121.code, self.account_1121.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '131',
                'date': date(2021, 10, 15),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
            },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'account_title',
                'account_name': '%s %s' % (self.account_131.code, self.account_131.name)
            },
            {
                'type': 'account_init',
                'name': 'Opening Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': 0,
                'progress_debit': 0,
                'progress_credit': 0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '5111',
                'date': date(2021, 10, 10),
                'debit': 500.0,
                'credit': 0.0,
                'progress_debit': 500.0,
                'progress_credit': 0.0,
                'progress': 500.0,
            },
            {
                'type': 'move_line',
                'name': None,
                'account_id': '1121',
                'date': date(2021, 10, 15),
                'debit': 0.0,
                'credit': 500.0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
            {
                'type': 'account_total',
                'name': 'Period Total',
                'account_id': '',
                'debit': 500.0,
                'credit': 500.0,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                },
            {
                'type': 'account_end',
                'name': 'Ending Balance',
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': 500.0,
                'progress_credit': 500.0,
                'progress': 0.0,
            },
        ]
        self.assertEqual(valid_lines, expected_values)
