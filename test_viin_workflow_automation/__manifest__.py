{
    'name': 'Workflow Automation',
    'name_vi_VN': 'Tự động hóa Quy trình',

    'summary': 'Visual Workflow Automation - Design, Execute & Monitor Business Processes',
    'summary_vi_VN': 'Tự động hóa Quy trình Trực quan - Thiết kế, Thực thi & Giám sát Quy trình Nghiệp vụ',

    'description': """
Problems
========
Managing complex business processes in Odoo often requires extensive custom development. Businesses struggle with:

- **Manual process tracking**: Employees manually track approval chains, causing delays and errors
- **Rigid automation rules**: Base automation lacks visual flow design and complex branching logic
- **Limited process visibility**: No real-time insight into where processes are stuck or who's responsible
- **Scattered process logic**: Business rules buried in code, making maintenance and updates difficult
- **Inconsistent execution**: Manual processes lead to different outcomes depending on who handles them

Solution
========
BPMN Workflow Engine brings enterprise-grade Business Process Model and Notation (BPMN 2.0) standard to Odoo, enabling visual workflow design and automated execution. Design once, execute consistently across your entire organization.

Key Features
============
#. **Visual Workflow Designer**

   - Drag-and-drop BPMN 2.0 diagram editor
   - Support for all major BPMN elements: Tasks, Gateways (Exclusive/Parallel/Inclusive/Event-Based), Events, Pools, Lanes
   - BPMN XML editing for diagram customization
   - Version control with draft/published workflow states

#. **Flexible Workflow Triggering**

   - Manual trigger: Launch workflows on-demand via button click or wizard
   - Event-based trigger: Automatically start workflows when records are created, updated, or meet specific conditions
   - Recurring trigger: Schedule workflows to run periodically (daily, weekly, monthly, yearly) with configurable recurrence patterns

#. **Intelligent Execution Engine**

   - BPMN 2.0 compliant execution with proper gateway semantics
   - State-driven execution with comprehensive error handling
   - Multiple execution modes: Automatic tasks with server actions, Manual tasks with user assignment, Event-driven tasks waiting for triggers
   - Priority-based node execution scheduling for critical path optimization

#. **Deep Odoo Integration**

   - Attach workflows to any Odoo model (Sale, Purchase, Project, etc.)
   - Execute Odoo server actions directly from workflow tasks
   - User/group assignment via pools and lanes with dynamic field-based assignment
   - Seamless integration with Odoo's activity system for manual task notifications
   - Real-time workflow state updates via bus notifications to all connected users

#. **Advanced Process Control**

   - Multiple concurrent workflow instances per record
   - Conditional routing with Odoo domain expressions for dynamic decisions
   - Embedded subprocesses (synchronous/asynchronous) for modular workflow design
   - Data associations for input/output parameter passing between nodes
   - Manual intervention: Retry failed nodes, skip nodes with approval permissions

#. **Comprehensive Monitoring & Auditing**

   - Complete execution history with action-level logging and error tracking
   - Visual workflow instance viewer with real-time state coloring (pending/running/success/failed)
   - Detailed failure messages with stack traces for debugging
   - Configurable log retention and automatic cleanup to manage database size
   - Progress tracking with percentage completion for long-running processes

#. **Enterprise Security & Access Control**

   - Role-based permissions: Admin (full control), Designer (create workflows), Approver (publish/retry/skip), Basic User (view only)
   - Model-based access control: users only see workflows for models they have permission to access
   - Record-level access control with Odoo's security rules
   - Lane/pool-based task assignment for organized workflow execution

Benefits
========
1. **Accelerated process automation**

   - Design complex workflows visually in hours, not weeks of coding
   - No-code/low-code approach empowers business analysts to automate processes without developer dependency

2. **Improved process visibility and control**

   - Real-time monitoring shows exactly where each process instance is and who's responsible
   - Identify bottlenecks instantly and optimize workflows based on execution data

3. **Reduced errors and inconsistencies**

   - Automated execution ensures every instance follows the exact same process
   - Retry mechanisms and error handling prevent data loss from transient failures

4. **Enhanced compliance and auditability**

   - Complete audit trail of every workflow execution with timestamps and responsible users
   - Version control maintains history of process changes for regulatory compliance

5. **Faster time-to-market for process changes**

   - Update workflows visually and publish new versions without code deployment
   - Test changes in draft mode before rolling out to production

6. **Scalable process management**

   - Handle hundreds of concurrent workflow instances with efficient state-driven execution
   - Subprocess support enables complex enterprise processes with reusable components

Technical Notes
===============
- **Built-in automation testing**: The module comes with **comprehensive automated test coverage** (instance execution, gateway logic, event handling, access control, subprocess execution), ensuring system quality and stability.
- **Easy maintenance and scalability**: With automated testing and modular architecture, businesses can upgrade or customize the module without disrupting existing operations.
- **Modern technology stack**: Built on Odoo OWL framework with bpmn-js for standards-compliant BPMN editing.
- **Performance optimized**: State-driven execution model (not token-based) minimizes database overhead and enables parallel execution.

Target Users
============
#. **Manufacturing companies**

   - Need to automate quality control workflows, production approval chains, and equipment maintenance processes

#. **Financial services organizations**

   - Require multi-step approval workflows for loans, credit applications, and compliance processes

#. **Healthcare and pharmaceutical companies**

   - Must track patient onboarding, treatment protocols, and regulatory compliance workflows

#. **Service-based businesses**

   - Want to automate customer onboarding, case management, and escalation workflows

#. **Project-driven organizations**

   - Need to standardize project approval, resource allocation, and milestone tracking processes

#. **Any Odoo user requiring**

   - Visual process design, complex conditional logic, multi-step approvals, or enterprise-grade workflow automation

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Vấn đề
======
Quản lý các quy trình nghiệp vụ phức tạp trong Odoo thường đòi hỏi phải phát triển tùy chỉnh tốn kém. Doanh nghiệp gặp khó khăn với:

- **Theo dõi quy trình thủ công**: Nhân viên phải tự theo dõi chuỗi phê duyệt, gây ra chậm trễ và sai sót
- **Quy tắc tự động hóa cứng nhắc**: Automation cơ bản thiếu thiết kế luồng trực quan và logic phân nhánh phức tạp
- **Hạn chế khả năng hiển thị quy trình**: Không có cái nhìn thời gian thực về vị trí quy trình bị kẹt hoặc ai chịu trách nhiệm
- **Logic quy trình phân tán**: Quy tắc nghiệp vụ bị chôn vùi trong code, khiến việc bảo trì và cập nhật khó khăn
- **Thực thi không nhất quán**: Quy trình thủ công dẫn đến kết quả khác nhau tùy thuộc vào người xử lý

Giải pháp
=========
BPMN Workflow Engine mang tiêu chuẩn Mô hình hóa và Ký hiệu Quy trình Nghiệp vụ (BPMN 2.0) chuẩn doanh nghiệp vào Odoo, cho phép thiết kế quy trình trực quan và thực thi tự động. Thiết kế một lần, thực thi nhất quán trên toàn tổ chức.

Tính năng Nổi bật
=================
#. **Trình Thiết kế Quy trình Trực quan**

   - Trình soạn thảo sơ đồ BPMN 2.0 kéo thả
   - Hỗ trợ đầy đủ các thành phần BPMN: Tasks, Gateways (Exclusive/Parallel/Inclusive/Event-Based), Events, Pools, Lanes
   - Chỉnh sửa BPMN XML để tùy chỉnh sơ đồ
   - Kiểm soát phiên bản với trạng thái nháp/đã xuất bản

#. **Kích hoạt Quy trình Linh hoạt**

   - Kích hoạt thủ công: Khởi chạy quy trình theo yêu cầu qua nút bấm hoặc wizard
   - Kích hoạt theo sự kiện: Tự động bắt đầu quy trình khi bản ghi được tạo, cập nhật hoặc đáp ứng điều kiện cụ thể
   - Kích hoạt định kỳ: Lập lịch quy trình chạy định kỳ (hàng ngày, hàng tuần, hàng tháng, hàng năm) với các mẫu lặp lại có thể cấu hình

#. **Công cụ Thực thi Thông minh**

   - Thực thi tuân thủ BPMN 2.0 với ngữ nghĩa cổng chính xác
   - Thực thi dựa trên trạng thái với xử lý lỗi toàn diện
   - Nhiều chế độ thực thi: Tác vụ tự động với hành động máy chủ, Tác vụ thủ công với phân công người dùng, Tác vụ dựa trên sự kiện chờ kích hoạt
   - Lập lịch thực thi nút dựa trên mức ưu tiên để tối ưu đường đi quan trọng

#. **Tích hợp Sâu với Odoo**

   - Gắn quy trình vào bất kỳ mô hình Odoo nào (Sale, Purchase, Project, v.v.)
   - Thực thi các hành động máy chủ Odoo trực tiếp từ các tác vụ quy trình
   - Phân công người dùng/nhóm qua hồ bơi và làn đường với phân công động dựa trên trường
   - Tích hợp liền mạch với hệ thống hoạt động Odoo cho thông báo tác vụ thủ công
   - Cập nhật trạng thái quy trình thời gian thực đến tất cả người dùng đang kết nối

#. **Kiểm soát Quy trình Nâng cao**

   - Nhiều phiên bản quy trình đồng thời trên mỗi bản ghi
   - Định tuyến có điều kiện với biểu thức miền Odoo cho quyết định động
   - Quy trình con nhúng (đồng bộ/bất đồng bộ) cho thiết kế quy trình mô-đun
   - Liên kết dữ liệu cho việc truyền tham số đầu vào/đầu ra giữa các nút
   - Can thiệp thủ công: Thử lại nút thất bại, bỏ qua nút với quyền phê duyệt

#. **Giám sát & Kiểm toán Toàn diện**

   - Lịch sử thực thi đầy đủ với ghi nhật ký cấp hành động và theo dõi lỗi
   - Trình xem phiên bản quy trình trực quan với tô màu trạng thái thời gian thực (đang chờ/đang chạy/thành công/thất bại)
   - Thông báo lỗi chi tiết với stack traces để debug
   - Giới hạn lưu giữ nhật ký có thể cấu hình và tự động dọn dẹp để quản lý kích thước database
   - Theo dõi tiến độ với phần trăm hoàn thành cho các quy trình chạy lâu

#. **Bảo mật & Kiểm soát Truy cập Doanh nghiệp**

   - Phân quyền dựa trên vai trò: Admin (toàn quyền), Thiết kế (tạo quy trình), Approver (xuất bản/thử lại/bỏ qua), Người dùng nội bộ (chỉ xem)
   - Kiểm soát truy cập dựa trên mô hình: người dùng chỉ thấy quy trình cho các mô hình họ có quyền truy cập
   - Kiểm soát truy cập cấp bản ghi với security rules của Odoo
   - Phân công tác vụ dựa trên lane/pool để tổ chức thực thi quy trình

Lợi ích
=======
1. **Tăng tốc tự động hóa quy trình**

   - Thiết kế quy trình phức tạp trực quan trong vài giờ, không phải vài tuần coding
   - Phương pháp no-code/low-code giúp chuyên viên phân tích nghiệp vụ tự động hóa quy trình mà không phụ thuộc vào lập trình viên

2. **Cải thiện khả năng hiển thị và kiểm soát quy trình**

   - Giám sát thời gian thực cho biết chính xác vị trí từng phiên bản quy trình và ai chịu trách nhiệm
   - Xác định điểm nghẽn ngay lập tức và tối ưu quy trình dựa trên dữ liệu thực thi

3. **Giảm lỗi và sự không nhất quán**

   - Thực thi tự động đảm bảo mọi phiên bản tuân theo cùng một quy trình chính xác
   - Cơ chế thử lại và xử lý lỗi ngăn mất dữ liệu do lỗi tạm thời

4. **Tăng cường tuân thủ và khả năng kiểm toán**

   - Dấu vết kiểm toán đầy đủ của mọi lần thực thi quy trình với dấu thời gian và người dùng chịu trách nhiệm
   - Kiểm soát phiên bản duy trì lịch sử các thay đổi quy trình để tuân thủ quy định

5. **Thời gian đưa thay đổi quy trình ra thị trường nhanh hơn**

   - Cập nhật quy trình trực quan và xuất bản phiên bản mới mà không cần triển khai code
   - Kiểm tra thay đổi ở chế độ nháp trước khi triển khai production

6. **Quản lý quy trình có khả năng mở rộng**

   - Xử lý hàng trăm phiên bản quy trình đồng thời với thực thi hiệu quả dựa trên trạng thái
   - Hỗ trợ quy trình con cho phép các quy trình doanh nghiệp phức tạp với các thành phần có thể tái sử dụng

Ghi chú Kỹ thuật
================
- **Tích hợp automation test**: Module đi kèm với **bộ kiểm thử tự động toàn diện** (thực thi phiên bản, logic cổng, xử lý sự kiện, kiểm soát truy cập, thực thi quy trình con), đảm bảo chất lượng và tính ổn định của hệ thống.
- **Dễ dàng bảo trì và mở rộng**: Với kiểm thử tự động và kiến trúc mô-đun, doanh nghiệp có thể nâng cấp hoặc tùy chỉnh module mà không làm gián đoạn hoạt động hiện tại.
- **Công nghệ hiện đại**: Được xây dựng trên framework Odoo OWL với bpmn-js để chỉnh sửa BPMN tuân thủ tiêu chuẩn.
- **Tối ưu hiệu năng**: Mô hình thực thi dựa trên trạng thái (không phải dựa trên token) giảm thiểu overhead database và cho phép thực thi song song.

Đối tượng Sử dụng
=================
#. **Công ty sản xuất**

   - Cần tự động hóa quy trình kiểm soát chất lượng, chuỗi phê duyệt sản xuất và quy trình bảo trì thiết bị

#. **Tổ chức dịch vụ tài chính**

   - Yêu cầu quy trình phê duyệt nhiều bước cho vay, đơn xin tín dụng và quy trình tuân thủ

#. **Công ty y tế và dược phẩm**

   - Phải theo dõi quy trình tiếp nhận bệnh nhân, phác đồ điều trị và quy trình tuân thủ quy định

#. **Doanh nghiệp dịch vụ**

   - Muốn tự động hóa quy trình tiếp nhận khách hàng, quản lý hồ sơ và quy trình leo thang

#. **Tổ chức định hướng dự án**

   - Cần chuẩn hóa quy trình phê duyệt dự án, phân bổ nguồn lực và theo dõi mốc quan trọng

#. **Bất kỳ người dùng Odoo nào yêu cầu**

   - Thiết kế quy trình trực quan, logic điều kiện phức tạp, phê duyệt nhiều bước hoặc tự động hóa quy trình chuẩn doanh nghiệp

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v17demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v17demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Workflow',
    'version': '0.1.0',
    'images': ['static/description/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'price': 279.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
