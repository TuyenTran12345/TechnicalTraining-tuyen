import json

from odoo import http
from odoo.http import content_disposition, request, serialize_exception
from odoo.tools import html_escape


class AccountReportController(http.Controller):

    @http.route('/to_account_reports', type='http', auth='user', methods=['POST'], csrf=False)
    def download_report(self, report_data, token, output_format='pdf', report_id=None, **kw):
        report_data = json.loads(report_data)
        try:
            company_id = int(kw.get('company_id'))
        except ValueError:
            company_id = []
        company = request.env['res.company'].browse(company_id).exists() or request.env.company
        Report = request.env['account.report'].with_user(request.session.uid).with_company(company)
        if report_id or report_id not in ('null', 'undefined'):
            try:
                report_id = int(report_id)
            except ValueError:
                report_id = False
        report = Report.browse(report_id)
        if not report:
            return request.not_found()
        file_name = report.get_export_filename()
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    '',
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition(file_name + '.xlsx'))
                    ]
                )
                response.stream.write(report.render_xlsx(report_data))
            else:
                response = request.make_response(
                    report._render_pdf(report_data),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', content_disposition(file_name + '.pdf'))
                    ]
                )
            response.set_cookie('fileToken', token)
            return response
        except Exception as e:
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': serialize_exception(e)
            }
            return request.make_response(html_escape(json.dumps(error)))
