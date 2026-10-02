# Nhật ký sử dụng AI trong lần xây dựng

## Yêu cầu của người dùng

Xây dựng hệ thống Django quản lý thuê căn hộ có tích hợp AI theo cấu trúc đã đọc, được điều chỉnh thống nhất với báo cáo Word. Người dùng chọn API tương thích OpenAI.

## Phần AI hỗ trợ tạo

- 10 app Django và 12 model theo ánh xạ báo cáo.
- Form, view, URL, giao diện tiếng Việt và kiểm tra vai trò.
- Service hợp đồng, cảnh báo, báo cáo, đọc tài liệu và gọi AI.
- Prompt tóm tắt, nhắc hạn, chatbot; test bằng mock cho timeout, JSON và nguồn.
- Script cài đặt, dữ liệu demo, sao lưu, README và sơ đồ.

## Nội dung đã rà soát trong mã nguồn

- Tiền cọc nằm trong Contract, không tạo model Deposit riêng.
- RegulationDocument có liên kết Regulation, tên/đường dẫn tệp và văn bản trích xuất.
- Nhân viên không xem tiền thanh toán qua thông báo AI hoặc cảnh báo tài chính.
- Kế toán cập nhật cọc qua form một trường, không sửa hợp đồng qua POST giả.
- Dữ liệu hợp đồng không phải chỉ thị dành cho AI; prompt có ràng buộc không tư vấn pháp lý.
- Các điểm ngoài mô tả chi tiết của Word được ghi tại docs/decisions.md.

## Phần nhóm sinh viên cần kiểm chứng

Đối chiếu thao tác và dữ liệu với báo cáo, thực hiện checklist demo, cấu hình dịch vụ AI rồi đánh giá chất lượng bằng dữ liệu hư cấu. Nhật ký này không khẳng định sinh viên đã review, không thay thế ảnh chạy thật và không coi mock là kết quả thử model thật.

## Cập nhật 23/09/2026

Lựa chọn OpenAI ở trên là lịch sử bản ban đầu. Theo ../requirements/ContextProject.txt mới bổ sung, cấu hình hiện hành chuyển sang Gemini. Xem synchronization.md để biết thay đổi và giới hạn xác minh.
