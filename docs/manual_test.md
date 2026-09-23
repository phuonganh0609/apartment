# Kịch bản demo và kiểm tra thủ công

Chạy setup, giữ mật khẩu demo được in ra và mở localhost. Các bước sau là checklist cần thực hiện, không phải kết quả đã xác nhận.

1. Đăng nhập quanly. Xem dashboard; đổi tháng và đối chiếu khoản thu.
2. Tạo tòa nhà/căn hộ, gán tiện ích và số lượng. Tìm/lọc/sắp xếp; kiểm tra trên màn hình hẹp.
3. Tạo khách thuê và người liên hệ; thử CCCD trùng hoặc sai số chữ số.
4. Lập hợp đồng đã ký. Thử tạo hợp đồng trùng căn và thời gian → phải báo lỗi.
5. Cập nhật tiền cọc; gia hạn hợp đồng; thử ngày kết thúc trước ngày bắt đầu.
6. Tạo khoản thu pending với hạn hôm qua. Khoản đó xuất hiện công nợ và cảnh báo quá hạn.
7. Chuyển paid, nhập ngày thực thu. Khoản đó rời công nợ và được cộng vào doanh thu đúng tháng.
8. Thanh lý hợp đồng còn công nợ → căn hộ không còn bị chiếm, khoản nợ vẫn giữ.
9. Tạo và cập nhật yêu cầu bảo trì từ mới sang đang xử lý/hoàn thành.
10. Đăng nhập nhanvien, nhập trực tiếp URL payments/reports/accounts → 403. Xác nhận vẫn dùng hợp đồng, bảo trì và AI tóm tắt.
11. Đăng nhập ketoan, mở hợp đồng xem được nhưng sửa/gia hạn bị chặn. Màn hình tiền cọc chỉ sửa cọc.
12. Tạo quy định và tải tệp TXT/DOCX/PDF có văn bản. Kiểm tra văn bản trích xuất và tải xuống có đăng nhập.
13. Khi chưa có cấu hình AI, thử tóm tắt → thông báo cấu hình rõ ràng, không có bản tóm tắt giả.
14. Sau khi cấu hình model thật, thử tóm tắt hợp đồng đủ/thiếu điều khoản, soạn thông báo, hỏi quy định có nguồn và câu ngoài phạm vi.
15. Sao chép thông báo sau khi chỉnh sửa; xác nhận không có email tự gửi.
16. Ngắt kết nối API hoặc dùng khóa thử không hợp lệ → ứng dụng báo lỗi, hợp đồng gốc không đổi.
17. Chạy backup_database; kiểm tra bản sao bằng SQLite `PRAGMA integrity_check` trước một lần diễn tập phục hồi trên bản sao môi trường.

Lưu ảnh demo thật vào docs/screenshots và kết quả thử prompt thật vào docs/ai_evidence. Không chụp khóa API, CCCD hoặc dữ liệu khách thuê thật.
