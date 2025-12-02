{
    'name': "Accounting Reports - Vietnam Accounting",
    'name_vi_VN': "Báo cáo kế toán - Kế toán Việt Nam",
    'old_technical_name': 'to_account_reports_l10n_vn',

    'summary': """
Default template financial reports for Vietnam""",
    'summary_vi_VN': """
Mẫu báo cáo tài chính mặc định dành cho các doanh nghiệp Việt Nam""",

    'description': """
Demo video: `Accounting Reports - Vietnam Accounting <https://youtu.be/hl0AJGFHjNU>`_

Key Features
============

#. Provide the chart of accounts according to No.200/2014/TT-BTC and Circular No.133/2016/TT-BTC of the Ministry of Finance of Vietnam.

#. Provide the following financial reports for companies based on the Vietnam following Vietnam Accounting Standard (VAS) and requirements from the Ministry of Finance (No.200/2014/TT-BTC and Circular No.133/2016/TT-BTC).

   * VAT Declaration;
   * Profit and Loss (B02-DN);
   * Balance Sheet (B01-DN);
   * Cash Flow Statement (B03-DN).

#. Provide PDF and Excel versions:

   * Account detail sheet that complies with Circular No. 200/2014/TT-BTC dated 22 December 2014 and Circular No. 133/2016/TT-BTC dated 01 January 2017 of the Ministry of Finance of Vietnam.
   * Accounting general ledger that complies with Circular No. 200/2014/TT-BTC dated 22 December 2014 and Circular No. 133/2016/TT-BTC dated 01 January 2017 of the Ministry of Finance of Vietnam.
   * Account Bank/Cash book complies with Circular No. 200/2014/TT-BTC dated 22 December 2014 and Circular No. 133/2016/TT-BTC dated 01 January 2017 of the Ministry of Finance of Vietnam.

#. Provide Excel version

   * Invoicing and Bills Declaration that complies with Circular No. 119/2014/TT-BTC dated 25 August 2014 of the Ministry of Finance of Vietnam.

Editions Supported
==================
1. Community Edition

    """,
    'description_vi_VN': """
Demo video: `Báo cáo kế toán - Kế toán Việt Nam <https://youtu.be/hl0AJGFHjNU>`_

Tính năng cơ bản
================

#. Cung cấp hệ thống tài khoản kế toán theo thông tư 200/2014/TT-BTC, thông 133/2016/TT-BTC.

#. Cung cấp các báo cáo tài chính tương thích với chuẩn mực kế toán Việt Nam và các yêu cầu của Bộ Tài chính như sau:

   * Tờ khai thuế giá trị gia tăng;
   * Kết quả hoạt động kinh doanh (B02-DN);
   * Bảng Cân đối Kế toán (B01-DN);
   * Báo cáo Lưu chuyển Tiền tệ (B03-DN).

#. Cung cấp phiên bản PDF và Excel

   * Sổ chi tiết tài khoản tuân thủ Thông tư số 200/2014/TT-BTC ngày 22 tháng 12 năm 2014, Thông tư 133/2016/TT-BTC ngày 01/01/2017 của Bộ Tài chính Việt Nam.
   * Sổ nhật ký chung tuân thủ Thông tư số 200/2014/TT-BTC ngày 22 tháng 12 năm 2014, Thông tư 133/2016/TT-BTC ngày 01/01/2017 của Bộ Tài chính Việt Nam.
   * Sổ quỹ tiền mặt và tiền gửi ngân hàng tuân thủ Thông tư số 200/2014/TT-BTC ngày 22 tháng 12 năm 2014, Thông tư 133/2016/TT-BTC ngày 01/01/2017 của Bộ Tài chính Việt Nam.

#. Cung cấp phiên bản Excel

   * Bảng kê hóa đơn, chứng từ bán ra (01-1/GTGT) theo thông tư 119/2014/TT-BTC ban hành ngày 25/08/2014 của Bộ Tài chính.
   * Bảng kê hóa đơn, chứng từ mua vào (01-2/GTGT) theo thông tư 119/2014/TT-BTC ban hành ngày 25/08/2014 của Bộ Tài chính.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/apps/app/16.0/l10n_vn_viin_account_reports',
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'demo_video_url': "https://youtu.be/hl0AJGFHjNU",
    'support': 'apps.support@viindoo.com',
    'category': 'Accounting/Localizations',
    'version': '0.1.8',
    'depends': ['to_account_reports', 'l10n_vn_viin', 'to_legal_invoice_number', 'viin_analytic_tag'],
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat_data.xml',
        'data/balance_sheet_c200_report_data.xml',
        'data/balance_sheet_c133_b01a_report_data.xml',
        'data/balance_sheet_c133_b01b_report_data.xml',
        'data/profit_and_loss_c200_report_data.xml',
        'data/profit_and_loss_c133_report_data.xml',
        'data/cash_flow_c200_report_data.xml',
        'data/cash_flow_c133_report_data.xml',
        # 'views/account_chart_template_views.xml',
        'views/account_report_view.xml',
        'views/account_report_templates_vn.xml',
        'views/report_l10n_vn_s38dn.xml',
        'views/report_l10n_vn_s03adn.xml',
        'views/report_l10n_vn_s03bdn.xml',
        'views/report_l10n_vn_s07dn.xml',
        'views/report_l10n_vn_s08dn.xml',
        'views/root_menu.xml',
        'wizards/l10n_vn_s38dn.xml',
        'wizards/l10n_vn_s03adn.xml',
        'wizards/l10n_vn_s03bdn.xml',
        'wizards/l10n_vn_s07dn.xml',
        'wizards/l10n_vn_s08dn.xml',
        'wizards/l10n_vn_c119_01gtgt.xml',
        'wizards/l10n_vn_c119_02gtgt.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    # 'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['to_account_reports', 'l10n_vn_viin'],
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
