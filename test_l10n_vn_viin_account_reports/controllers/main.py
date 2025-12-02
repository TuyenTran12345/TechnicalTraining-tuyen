from odoo import http, _
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError


class ReportController(http.Controller):

    def download_excel(self, wizard_id, res_model, file_name, method_print_excel='report_excel'):
        """Method use download excel
        :return: file excel"""
        res_wizard = request.env[res_model].browse(wizard_id)
        if not res_wizard.exists():
            raise AccessError(_('Record not found: id: %s, uid: %s') % (wizard_id, request.env.user.id))
        file_data = getattr(res_wizard, method_print_excel)()
        content_length = len(file_data.getvalue())
        http_headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Length', content_length),
            ('Content-Disposition', content_disposition(file_name))
             ]
        return request.make_response(file_data, headers=http_headers)

    @http.route('/account-detail-sheet/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def l10n_vn_s38dn_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Account Detail Sheet.xlsx')
        res_model = 'l10n_vn.s38dn'
        return self.download_excel(wizard_id, res_model, file_name)

    @http.route('/account-cash-book/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def l10n_vn_s07dn_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Account Cash Book.xlsx')
        res_model = 'l10n_vn.s07dn'
        return self.download_excel(wizard_id, res_model, file_name)

    @http.route('/account-bank-book/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def l10n_vn_s08dn_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Account Bank Book.xlsx')
        res_model = 'l10n_vn.s08dn'
        return self.download_excel(wizard_id, res_model, file_name)

    @http.route('/general-journal/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def l10n_vn_s03adn_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('General Journal S03a-DN.xlsx')
        res_model = 'l10n_vn.s03adn'
        return self.download_excel(wizard_id, res_model, file_name)

    @http.route('/ledger/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def l10n_vn_s03bdn_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Ledger S03b-DN.xlsx')
        res_model = 'l10n_vn.s03bdn'
        return self.download_excel(wizard_id, res_model, file_name)

    @http.route('/invoice-declaration-sales/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c119_01gtgt_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Invoice Declaration Sales.xlsx')
        res_model = 'l10n_vn.c119.01gtgt'
        return self.download_excel(wizard_id, res_model, file_name, 'export_excel_sale')

    @http.route('/invoice-declaration-purchase/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c119_02gtgt_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Invoice Declaration Puchases.xlsx')
        res_model = 'l10n_vn.c119.02gtgt'
        return self.download_excel(wizard_id, res_model, file_name, 'export_excel_purchase')
