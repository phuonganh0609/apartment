# Bộ tài liệu quy định Nestora v1.0

Ngày áp dụng trong demo: 30/10/2026. Đây là quy trình mô phỏng cho đồ án,
không phải văn bản chính thức của Vinhomes hoặc hợp đồng đã ký.

Nạp dữ liệu bằng `.venv/Scripts/python.exe -X utf8 manage.py seed_rental_regulations`.
Lệnh tạo 12 quy định và 12 tệp Markdown đính kèm, trích xuất nội dung cho RAG;
chạy lại giữ nguyên bản ghi đã có, không sửa nội dung người dùng đã chỉnh.
Nguồn có thể chỉnh tại `data/rental_regulations.json` trước lần nạp đầu tiên.
Tệp thực tế lưu trong kho tài liệu riêng của ứng dụng, tải qua trang chi tiết quy định.

| Mã | Chủ đề | Người được tra cứu |
| --- | --- | --- |
| NT-01 | Đăng ký thuê và ký hợp đồng | Công khai, các vai trò |
| NT-02 | Tiền thuê, phí quản lý, thanh toán | Khách thuê và nhân sự |
| NT-03 | Tiền cọc, khấu trừ, hoàn cọc | Khách thuê và nhân sự |
| NT-04 | Gia hạn, chấm dứt, trả căn | Khách thuê và nhân sự |
| NT-05 | Sinh hoạt, tiếng ồn, thú cưng | Khách thuê và nhân sự |
| NT-06 | Báo hỏng, bảo trì | Khách thuê và nhân sự |
| NT-07 | Thẻ cư dân, khách thăm, chuyển đồ | Khách thuê và nhân sự |
| NT-08 | Gửi xe, điện nước, dịch vụ riêng | Khách thuê và nhân sự |
| NT-09 | Tiện ích chung, vệ sinh | Khách thuê và nhân sự |
| NT-10 | Cổng khách thuê, AI, email, thông tin | Khách thuê và nhân sự |
| NV-01 | Quy trình kiểm kê và bàn giao | Quản lý, nhân viên, admin |
| KT-01 | Quy trình đối soát công nợ và cọc | Quản lý, kế toán, admin |

Đăng nhập `quanly` để xem đầy đủ tại `/regulations/`, mở chi tiết và tải tệp.
Chatbot khách thuê chỉ truy xuất nội dung công khai và nội dung dành cho khách thuê.
Câu hỏi thử và ý cần có nằm trong các trường `question`, `expected` của dữ liệu nguồn.
Kiểm tra kết quả AI có trích nguồn hỗ trợ, không chỉ kiểm tra câu trả lời nghe hợp lý.

Các mức cố định dùng cho demo: phí quản lý 12.000 đồng/m²/tháng;
cọc 2 tháng tiền thuê; hạn tiền thuê/phí quản lý ngày 05;
báo gia hạn 30 ngày trước hết hạn; hoàn cọc trong 7 ngày làm việc sau đối soát
và bàn giao; yên tĩnh 22h–6h. Điện nước theo hóa đơn, không tự đặt đơn giá.
Các khoản trên không được tự áp dụng để sửa hợp đồng hay khoản thu đã tạo.
