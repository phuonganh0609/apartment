# Quyền giao diện theo bốn vai trò — 27/10/2026

Áp dụng theo ảnh người dùng cung cấp. Menu bị ẩn vẫn được bảo vệ ở backend.

| Vai trò | Giao diện được dùng |
|---|---|
| Quản lý | Toàn bộ vận hành, tài chính, báo cáo, tài khoản, quy định và AI |
| Nhân viên | Căn hộ/tòa nhà/tiện ích, khách/liên hệ, hợp đồng, bảo trì, cảnh báo vận hành và AI liên quan; không có menu tiền cọc/tài chính/báo cáo |
| Kế toán | Thanh toán tiền thuê/phí dịch vụ, tiền cọc, công nợ, báo cáo doanh thu, cảnh báo tài chính; hợp đồng được đọc để đối soát qua liên kết tài chính, không sửa nghiệp vụ |
| Khách thuê | Căn hộ của tôi: thông tin thời hạn hợp đồng, nhắc khoản chưa thu, gửi và theo dõi yêu cầu bảo trì của mình |

Nhân viên và kế toán không được xóa dữ liệu qua CRUD chung. Cập nhật cọc dành cho quản lý hoặc kế toán được bật quyền cập nhật cọc. AI/quy định nội bộ được giữ cho ba vai trò vận hành; khách thuê không có quyền truy cập.

Khách thuê cần được liên kết với hồ sơ Tenant qua trang quản lý tài khoản. Không tự suy luận liên kết bằng tên/email. Form bảo trì chỉ nhận căn hộ thuộc hợp đồng đang hiệu lực của hồ sơ đó, không nhận trạng thái xử lý/ghi chú từ khách. Danh sách yêu cầu lọc theo người gửi, thông báo thanh toán lọc theo hợp đồng của chính khách.

Thông báo hiện hiển thị trong cổng khách thuê, không tự gửi email/SMS. Tài khoản chưa liên kết không xem được dữ liệu thuê của người khác.

Đã bổ sung migration accounts/maintenance và test phân quyền, menu, giả mạo căn hộ/trạng thái, tài khoản chưa liên kết. Hồ sơ mô tả chỉ ba vai trò trước đây là lịch sử trước lần thay đổi này.

## Quyền AI cập nhật

- Trên form hợp đồng, Admin/Quản lý chọn “Người được sử dụng AI trên hợp đồng”. Nhân viên không thể tự sửa danh sách này.
- Tóm tắt: nội bộ (kể cả superuser) phải có tên trong phân công; khách thuê chỉ hợp đồng liên kết đúng Tenant của mình.
- Nhắc thanh toán: quản lý/kế toán trên hợp đồng được phân công; nhân viên hoặc Admin cần bật quyền bổ sung trên tài khoản.
- Nhắc gia hạn: quản lý trên hợp đồng được phân công; nhân viên/kế toán/Admin cần bật quyền bổ sung.
- Khách thuê không soạn thông báo. Quyền chatbot giữ lọc theo phạm vi tài liệu.
- Hợp đồng cũ không tự gán quyền AI đại trà. Quản lý cần phân công trước khi sử dụng. Chưa mở chatbot công khai.
