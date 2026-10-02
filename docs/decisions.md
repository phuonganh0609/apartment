# Đối chiếu báo cáo và quyết định triển khai

Nguồn hiện hành: requirements/ContextProject.txt (kiến trúc và công nghệ), requirements/informember.md (nghiệp vụ và tiêu chí chấm), requirements/project.md (thông tin nhóm). Các quyết định dưới đây cụ thể hóa những điểm tài liệu chưa quy định. Giữ cấu trúc sáu thư mục theo yêu cầu trực tiếp của người dùng.

| Lớp Word | Model Django | App |
|---|---|---|
| TaiKhoan | User | accounts |
| ToaNha | Building | buildings |
| CanHo | Apartment | buildings |
| TienIch | Amenity | buildings |
| KhachThue | Tenant | tenants |
| NguoiLienHe | Contact | tenants |
| HopDong | Contract | contracts |
| ThanhToan | Payment | payments |
| YeuCauBaoTri | MaintenanceRequest | maintenance |
| QuyDinh | Regulation | regulations |
| TienIchCanHo | ApartmentAmenity | buildings |
| TaiLieuQuyDinh | RegulationDocument | regulations |

`id` tự sinh là khóa chính. Các tên tiếng Anh ánh xạ cùng ý nghĩa với thuộc tính tiếng Việt trong Word. User kế thừa AbstractUser, sử dụng username/password/is_active cho tên đăng nhập, mật khẩu băm và trạng thái. Tên file và đường dẫn tài liệu được biểu diễn bằng filename và FileField; extracted_content lưu văn bản trích xuất.

## Các quyết định

1. Django Templates và Bootstrap thay cho frontend SPA; config chứa helpers form/CRUD để hạn chế lặp. App nghiệp vụ nằm trong backend; templates tập trung ở frontend/templates; định nghĩa model ở models và được app xuất lại để Django nhận diện. Giữ app_label và migrations cũ. Service nghiệp vụ và AI tách riêng.
2. Nội dung hợp đồng là TextField `contract_content`. Người dùng nhập văn bản khi lập hợp đồng. Thư mục data/media/contracts được giữ theo cấu trúc, hiện chưa có luồng tải tệp hợp đồng.
3. Tiền cọc là `deposit_amount` trong Contract. Tạo hợp đồng mặc định cọc bằng 0; người có quyền dùng màn hình tiền cọc riêng để cập nhật. Kế toán không thể dùng màn hình này để sửa các trường khác.
4. Payment không có bảng giao dịch con hoặc thanh toán một phần. Một khoản được nhận toàn bộ hoặc chưa thu. Khóa duy nhất (contract, kind, due_date) chống trùng khoản cùng loại, cùng hạn; phí dịch vụ cùng hạn được tổng hợp một khoản.
5. Trạng thái hợp đồng: draft, active (đã ký), terminated. Hợp đồng quá ngày kết thúc tự không còn chiếm căn hộ khi truy vấn; giữ trạng thái đã ký trong lịch sử. Ngày hết hạn là ngày vẫn thuộc thời gian thuê.
6. Trạng thái vận hành căn hộ: available, maintenance. Tình trạng “Đang cho thuê” suy ra từ hợp đồng có hiệu lực theo ngày, tránh một trường occupied bị lỗi thời.
7. Doanh thu bằng tổng Payment đã thanh toán trong tháng dựa trên paid_date; công nợ bằng tổng Payment pending. Tiền cọc không được cộng vào doanh thu. Thanh lý không xóa các khoản chưa thu.
8. Quản lý có quyền quản trị tài khoản/tài liệu. Nhân viên và Kế toán xem quy định và chatbot. Quyền tài chính không cấp cho Nhân viên. Dashboard của Nhân viên là danh sách việc cần làm, không phải báo cáo tài chính/công suất.
9. Các ngày/số tiền được kiểm tra cả tại form/model; CSDL có constraint cho ngày, tiền, liên kết tiện ích và tính nhất quán trạng thái thanh toán. Dữ liệu có hợp đồng tham chiếu dùng PROTECT khi xóa.
10. AI mặc định dùng Google Gemini API theo requirements/ContextProject.txt; OpenAI-compatible và Ollama là tùy chọn. Không ghi lại prompt chứa dữ liệu khách thuê trong log. Prompt hệ thống, services và xử lý lỗi tách khỏi views. Chưa có kết quả gọi model thật khi chưa cấu hình khóa/model.
11. RAG từ khóa bỏ dấu, đoạn 1.300 ký tự, bước 1.000, tối đa 4 nguồn; chỉ dùng Regulation đang áp dụng. Trả thiếu thông tin nếu không có nguồn, kiểm tra ID trích dẫn từ AI. Kiểm tra ID nguồn không tự chứng minh câu trả lời hoàn toàn chính xác; người dùng đối chiếu văn bản.
12. Kiểm thử concurrency thực tế PostgreSQL, triển khai production và đánh giá chất lượng model cần môi trường/dịch vụ tương ứng; không thay thế bằng kết quả mock.

## Phân quyền

| Nghiệp vụ | Quản lý | Nhân viên | Kế toán |
|---|---|---|---|
| Căn hộ, tiện ích, khách thuê | CRUD | CRUD | Xem |
| Hợp đồng | Tạo/sửa/gia hạn/thanh lý | Tạo/sửa/gia hạn/thanh lý | Xem |
| Cập nhật tiền cọc | Có | Khi cấp quyền riêng | Khi cấp quyền riêng |
| Thanh toán/công nợ | Có | Không | Có |
| Bảo trì | Có | Có | Không |
| Cảnh báo | Hợp đồng và thanh toán | Hợp đồng | Thanh toán |
| Báo cáo tài chính | Có | Không | Có |
| Công suất thuê | Có | Không | Không |
| AI tóm tắt | Có | Có | Không |
| AI nhắc gia hạn | Có | Có | Có |
| AI nhắc thanh toán | Có | Không | Có |
| Chatbot/quy định | Xem | Xem | Xem |
| Sửa quy định/tải tài liệu | Có | Không | Không |
| Quản lý tài khoản | Có | Không | Không |
