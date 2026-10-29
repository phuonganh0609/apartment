# Tra cứu dữ liệu hệ thống từ chatbot

Chatbot kết hợp hai đường xử lý:

- Câu hỏi trạng thái thực tế được nhận diện qua các nhóm từ khóa và gọi hàm ORM cố định.
  Kết quả được định dạng trực tiếp từ cơ sở dữ liệu, không gửi thông tin tài chính,
  nội dung bảo trì hoặc hợp đồng tới model AI để diễn giải.
- Câu hỏi quy trình, nội quy tiếp tục tìm tài liệu RAG theo quyền và gọi AI như trước.

Chức năng dữ liệu trực tiếp không chạy SQL do AI/người dùng cung cấp, không sửa dữ liệu,
không gửi thư, không xác nhận thanh toán hay tự gia hạn. Không cần khóa API cho đường
tra cứu trực tiếp; đường trả lời tài liệu vẫn cần cấu hình AI.

## Câu hỏi thử

| Câu hỏi | Nguồn/ý nghĩa |
| --- | --- |
| Có căn hộ nào còn trống dưới 8 triệu không? | Căn sẵn sàng, tòa hoạt động, không có hợp đồng hiệu lực hôm nay, giá dưới 8 triệu |
| Tòa S1.01 còn căn nào trống? | Lọc tên tòa có mã S1.01 |
| Tòa S1.01 có tiện ích gì? | Danh mục thiết bị trong từng căn, không suy ra tiện ích chung của tòa |
| Căn 0501 tòa S1.03 có tiện ích gì? | Số lượng thiết bị đã gán cho căn |
| Hợp đồng của tôi hết hạn ngày nào? | Hợp đồng gắn hồ sơ khách đang đăng nhập |
| Hợp đồng HD-NESTORA-019 hết hạn ngày nào? | Lọc đúng mã, trong phạm vi được xem |
| Danh sách hợp đồng sắp hết hạn | Hợp đồng đã ký, hết hạn trong 30 ngày tới |
| Tháng này tôi còn nợ bao nhiêu? | Tổng khoản chưa thu theo tháng đến hạn |
| Các khoản tiền thuê chưa thanh toán tháng 10/2026 | Lọc loại tiền thuê, kỳ đến hạn 10/2026 |
| Các khoản đã thanh toán của tôi | Số tiền và ngày thu thực tế |
| Yêu cầu bảo trì của tôi xử lý đến đâu? | Trạng thái, ưu tiên, ghi chú xử lý |
| Quy định hoàn cọc là gì? | Tra cứu tài liệu, không phải tra cứu số dư riêng |

Nguồn dữ liệu trực tiếp ghi thời điểm tra cứu theo múi giờ Django, hiển thị tối đa
10 căn/hợp đồng/khoản thu/yêu cầu. Tổng tiền tính toàn bộ khoản phù hợp, không chỉ
10 dòng hiển thị. Cần nêu mã tòa/căn/hợp đồng hoặc tháng để thu hẹp kết quả.
Nếu không nêu tháng, kết quả công nợ tính tất cả kỳ; nếu chỉ nêu số tháng, dùng năm hiện tại.
Kỳ thanh toán tính theo hạn thu, không phải tháng doanh thu theo ngày thu thực tế.

## Phân quyền

- Khách thuê: hợp đồng/khoản thu thuộc hồ sơ liên kết; bảo trì do chính tài khoản gửi.
  Danh mục căn trống chỉ hiển thị tin được công khai; tiện ích bổ sung được xem ở căn
  bản thân đang thuê. Không có liên kết hồ sơ thì không có dữ liệu hợp đồng/công nợ riêng.
- Quản lý/Admin: dữ liệu nghiệp vụ theo quyền đọc của hệ thống.
- Nhân viên: căn hộ, hợp đồng, bảo trì; không truy cập khoản thu/công nợ.
- Kế toán: danh mục căn hộ công khai, hợp đồng và thanh toán; không truy cập yêu cầu bảo trì.
- Tài khoản chưa đăng nhập, bị khóa hoặc vai trò lạ không được truy cập dữ liệu riêng.

Các truy vấn luôn lọc quyền trước khi tổng hợp và dựng câu trả lời. Nêu mã hợp đồng
khách khác hoặc yêu cầu bỏ qua quyền không mở rộng được dữ liệu. Không trả CCCD,
số điện thoại, email hoặc nội dung hợp đồng đầy đủ qua đường tra cứu này.

## Giới hạn

Nhận diện câu hỏi hiện theo nhóm từ khóa tiếng Việt có bỏ dấu, không phải hiểu mọi
cách diễn đạt. Chưa có bộ lọc tùy ý, lịch thuê tại ngày bất kỳ hoặc báo cáo doanh thu
trực tiếp qua chatbot. Căn trống tính tại hôm nay; cần kiểm tra lịch thuê tương lai
trước khi ký. Tiện ích chung như hồ bơi/gym tiếp tục lấy từ tài liệu, không suy ra
từ thiết bị của căn hộ. Chưa hỗ trợ ngữ cảnh hội thoại nhiều lượt; hãy nhắc lại mã
trong từng câu hỏi cần tra cứu.
