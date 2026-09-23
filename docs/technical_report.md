# Báo cáo kỹ thuật — Hệ thống quản lý thuê căn hộ có tích hợp AI

Nhóm 02 · CNTT K23K · Khoa Công nghệ thông tin · Trường Đại học Công nghệ thông tin và Truyền thông.
Nguyễn Phương Anh: Trưởng nhóm. Lừu Thị Huệ: Phó nhóm.
Bản mô tả hiện trạng phần mềm; kết quả thực nghiệm AI và xác nhận của sinh viên cần bổ sung sau khi thực hiện.

## 1. Bài toán và phạm vi

Đơn vị cho thuê cần thay bảng tính bằng hệ thống tập trung để giảm sai sót lịch thuê, hạn thu tiền và xử lý bảo trì. Ba actor là Quản lý, Nhân viên, Kế toán. Khách thuê là đối tượng được quản lý, chưa có tài khoản tự phục vụ. Nhân viên tiếp nhận yêu cầu bảo trì thay khách.

## 2. Actor và use case

| Actor | Quyền chính | Giới hạn |
|---|---|---|
| Quản lý | Quản trị tài khoản, danh mục, hợp đồng, thu tiền, bảo trì, báo cáo và quy định | Kiểm tra ràng buộc dữ liệu khi sửa/xóa |
| Nhân viên | Căn hộ, khách thuê, hợp đồng, bảo trì, tóm tắt và chatbot | Không xem tài chính; sửa cọc khi được cấp quyền riêng |
| Kế toán | Thanh toán, công nợ, báo cáo tài chính, nhắc hạn, chatbot | Không sửa hợp đồng; sửa cọc khi được cấp quyền riêng |

Tất cả use case nghiệp vụ yêu cầu đăng nhập; quyền kiểm tra ở backend. Xem ma trận chi tiết trong decisions.md.

| Use case | Đầu vào | Xử lý và ngoại lệ | Đầu ra |
|---|---|---|---|
| UC01 Đăng nhập | Tên tài khoản, mật khẩu | Xác thực, kiểm tra khóa tài khoản và giới hạn đăng nhập | Phiên đăng nhập hoặc lỗi |
| UC02 Quản lý tòa nhà/căn hộ/tiện ích | Mã, diện tích, giá, tòa nhà, tiện ích | Kiểm tra tiền, diện tích, mã duy nhất; không xóa dữ liệu đang tham chiếu | Danh sách, chi tiết, tình trạng thuê |
| UC03 Quản lý khách thuê/liên hệ | Họ tên, CCCD, điện thoại, quan hệ | Kiểm tra định dạng, CCCD trùng, quyền người dùng | Hồ sơ khách thuê và liên hệ |
| UC04 Lập/sửa hợp đồng | Căn hộ, khách, ngày thuê, nội dung | Kiểm tra ngày và trùng lịch; căn bảo trì không được ký | Hợp đồng và lịch chiếm căn |
| UC05 Gia hạn/thanh lý/cọc | Ngày hết hạn mới, thao tác thanh lý hoặc số cọc | Kiểm tra lịch và quyền riêng của tiền cọc; bảo toàn công nợ | Hợp đồng cập nhật, căn được giải phóng khi thanh lý |
| UC06 Theo dõi thanh toán | Hợp đồng, loại thu, số tiền, hạn, ngày thu | Không trùng loại+hạn; thu toàn bộ hoặc chưa thu | Khoản thu, công nợ và doanh thu |
| UC07 Bảo trì | Căn hộ, nội dung, ưu tiên, trạng thái | Tiếp nhận, cập nhật tiến độ và ghi chú | Danh sách yêu cầu cần xử lý |
| UC08 Cảnh báo | Ngày hiện tại và dữ liệu hợp đồng/khoản thu | Lọc hợp đồng sắp hết hạn, khoản chưa thu quá hạn theo vai trò | Danh sách cảnh báo trên web |
| UC09 Báo cáo | Tháng báo cáo | Tổng khoản đã thu theo ngày thu; tỷ lệ căn có hợp đồng trong ngày | Doanh thu, công nợ, công suất |
| UC10 Quản lý quy định | Nội dung, tệp TXT/MD/DOCX/PDF văn bản | Kiểm tra tệp, trích xuất, bảo vệ tải xuống bằng đăng nhập | Nguồn nội bộ cho RAG |
| UC11 Tóm tắt hợp đồng | Nội dung xem trước đã che dữ liệu cá nhân đã biết | Gemini tạo JSON 5 mục; kiểm tra định dạng; xử lý lỗi API | Thời hạn, thuê, cọc, nghĩa vụ thu, chấm dứt |
| UC12 Soạn thông báo | Hợp đồng hoặc khoản phải thu | Kiểm tra quyền tài chính, tạo subject/body | Bản nháp để sửa/sao chép; không tự gửi |
| UC13 Chatbot | Câu hỏi quy định | RAG lấy tối đa 4 đoạn; thiếu nguồn thì không gọi AI; xác minh ID nguồn | Câu trả lời kèm nguồn hoặc báo thiếu thông tin |

### Luồng chi tiết UC04

Tiền điều kiện: Quản lý/Nhân viên đã đăng nhập, có căn hộ và khách thuê.
1. Chọn khách, căn, ngày bắt đầu/kết thúc và nội dung hợp đồng.
2. Form kiểm tra ngày, model/service kiểm tra trạng thái tòa nhà/căn và giao nhau lịch thuê.
3. Lưu trong transaction; hiển thị thông báo và chi tiết hợp đồng.
Ngoại lệ: dữ liệu sai/trùng lịch/bận CSDL trả lỗi để sửa; không tự tạo bản ghi thay thế.
Hậu điều kiện: hợp đồng đã ký chỉ chiếm căn trong khoảng ngày, bao gồm ngày kết thúc.

### Luồng chi tiết UC13

Tiền điều kiện: đăng nhập một trong ba vai trò. Người dùng gửi câu hỏi.
1. Kiểm tra độ dài và giới hạn lượt gọi.
2. Chuẩn hóa tiếng Việt, tách đoạn quy định đang áp dụng và nội dung đính kèm.
3. Xếp hạng từ khóa; không có nguồn phù hợp thì trả thiếu thông tin.
4. Gửi nguồn và câu hỏi tới Gemini, nhận JSON answer/sources.
5. Kiểm tra ID trích dẫn thuộc tập nguồn gửi đi, hiển thị câu trả lời và trích đoạn.
Ngoại lệ: timeout, rate limit, thiếu cấu hình, bị chặn, JSON sai được báo rõ; không tạo đáp án giả.

## 3. Kiến trúc và cơ sở dữ liệu

backend chứa app Django theo nghiệp vụ; frontend chứa templates và tài nguyên; models chứa 12 lớp ORM; data chứa SQLite/media; chatbot chứa adapter, prompt và view AI; RAG truy xuất nguồn. manage.py và project_paths.py thiết lập import. Tên app trong Context là ví dụ: buildings tương ứng apartments, alerts tương ứng notifications, ai_assistant tương ứng ai_services.

| Model | Khóa/quan hệ chính | Ràng buộc và ý nghĩa |
|---|---|---|
| User | id; username duy nhất | Vai trò và quyền cọc; mật khẩu băm |
| Building | id; name duy nhất | Cờ hoạt động |
| Apartment | id; building_id | Mã duy nhất trong tòa; diện tích dương, giá không âm |
| Amenity | id; name duy nhất | Danh mục tiện ích |
| ApartmentAmenity | id; apartment_id, amenity_id | Cặp liên kết duy nhất, số lượng dương |
| Tenant | id; identity_number duy nhất | CCCD 12 số, xác thực điện thoại |
| Contact | id; tenant_id | Người liên hệ thuộc khách thuê |
| Contract | id; code duy nhất; apartment_id, tenant_id | Ngày kết thúc sau bắt đầu, cọc không âm, chống trùng lịch trong service |
| Payment | id; contract_id | Số tiền dương, trạng thái/ngày thu nhất quán, loại+hạn duy nhất mỗi hợp đồng |
| MaintenanceRequest | id; apartment_id | Trạng thái, ưu tiên và ghi chú xử lý |
| Regulation | id | Nội dung, loại, thời điểm cập nhật, cờ áp dụng |
| RegulationDocument | id; regulation_id | Tệp riêng tư, nội dung trích xuất |

ERD và luồng kiến trúc: diagrams/architecture.md. Tiền cọc là thuộc tính Contract, không bắt buộc bảng riêng. Doanh thu không gồm cọc. SQLite phục vụ demo; PostgreSQL có cấu hình nhưng chưa xác minh tải đồng thời.

## 4. Phi chức năng

- Bảo mật: authentication, authorization, CSRF, ORM, template escaping, password hashing; tệp tải xuống qua view xác thực.
- Riêng tư: che giá trị cá nhân đã biết trước khi tóm tắt, cho xem trước; không bảo đảm phát hiện toàn bộ dữ liệu tự do. Khóa chỉ ở môi trường cục bộ.
- Ổn định: giới hạn upload 5 MB, giới hạn dữ liệu AI, timeout và rate limit; phân trang danh sách. Chưa có kết quả đo tải production.
- Sao lưu: backup_database tạo snapshot SQLite; sao lưu data/media riêng; phục hồi theo README và kiểm tra trên bản sao.
- Giao diện: tiếng Việt, điều hướng theo vai trò, form báo lỗi, lọc/tìm/sắp xếp theo loại dữ liệu. Cần hoàn thành checklist màn hình hẹp trong manual_test.md.

## 5. AI và kiểm thử

Gemini REST generateContent nhận systemInstruction và dữ liệu JSON, yêu cầu phản hồi application/json. Khóa Gemini dùng biến riêng GEMINI_API_KEY. Cấu hình AI_MODEL theo model tài khoản có quyền dùng. Không tư vấn pháp lý vượt nguồn; thông báo luôn là bản nháp.

Tests trong backend/tests bao phủ hợp đồng, thu tiền, cảnh báo, phân quyền, tài liệu và AI mock. Mock kiểm tra logic/giao thức, không chứng minh chất lượng model thật. Kế hoạch và mẫu ghi kết quả ba vòng: prompts/evaluation.md. Tình trạng chạy: verification.md.

## 6. AI trong SDLC và kế hoạch hoàn thiện

AI đã hỗ trợ đọc yêu cầu, ánh xạ model, triển khai adapter và tạo kiểm thử; chi tiết trong ai_evidence/synchronization.md. Nhóm cần kiểm chứng, ghi nhận phản hồi và chỉnh sửa thực tế.

KT1: dùng use case/ERD/ma trận làm nền, nhóm duyệt lại nghiệp vụ. KT2: chạy demo CRUD và quyền, chụp kết quả thật. KT3: cấu hình Gemini, chạy ít nhất ba vòng, ghi chất lượng và sửa prompt từ kết quả. Cuối kỳ: bổ sung kết quả đo, ảnh demo, nhận xét nhóm vào báo cáo này và chuẩn bị thuyết trình. Không coi kế hoạch là minh chứng đã thực hiện.
