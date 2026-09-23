# Rà soát dự án — 23/09/2026

## Kết quả kiểm tra

- 60/60 tests đạt, thời gian 8,622 giây; dùng CSDL thử nghiệm.
- Django check, migration dry-run, pip check, Black và pycodestyle: đạt.
- Kiểm tra tĩnh: 135 file Python, 10 app, 12 model và CSRF trong form POST.
- Biên dịch 61 template: đạt; CSS, JS và Bootstrap được tìm thấy. Bootstrap được import từ style.css.
- SQLite integrity_check: ok; không vi phạm khóa ngoại, không có hợp đồng active trùng thời gian cùng căn.
- Dữ liệu hiện tại: 3 tài khoản, 16 căn, 10 khách, 10 hợp đồng, 30 khoản thu; chưa có tài liệu đính kèm quy định.
- Gemini check_ai_connection.py: PASS với dữ liệu hư cấu.
- Không thay đổi mã nghiệp vụ. Thử xóa tài liệu sử dụng InMemoryStorage và transaction rollback; không giữ bản ghi thử.

## Phát hiện cần xử lý

### P2 — RAG nhận nguồn không liên quan cho câu ngoài phạm vi

Vị trí: RAG/rag_service.py, tính điểm và ngưỡng 0.25.
Tái hiện trên dữ liệu hiện có: retrieve('Giá cổ phiếu hôm nay?') trả 2 nguồn:
Giờ yên tĩnh (từ trùng 'nay') và Gia hạn và bàn giao (từ 'gia').
Bỏ dấu làm 'giá' và 'gia' trùng nhau; ngưỡng chỉ một từ trên bốn đủ nhận nguồn.
Hậu quả: gọi model không cần thiết và có nguy cơ dùng nguồn không liên quan. Chưa khẳng định Gemini đã trả lời sai; phát hiện nằm ở retrieval.
Đề xuất: đánh giá mức liên quan bằng bộ câu hỏi có nguồn/ngoài phạm vi, loại từ phổ biến và thêm tiêu chí phù hợp trước khi gọi AI. Test hiện tại dùng ít dữ liệu nên không phát hiện trường hợp này.

### P2 — Lỗi ghi tệp khi upload thoát ra thành HTTP 500

Vị trí: backend/regulations/views.py:38, form.save không có xử lý lỗi lưu trữ/CSDL.
Tái hiện bằng RequestFactory và mock form hợp lệ với save ném OSError: exception thoát khỏi view.
Khi hết dung lượng hoặc mất quyền thư mục media, người dùng không nhận lỗi form để thử lại.
Đề xuất: xử lý lỗi dự kiến, thông báo an toàn và dọn tệp nếu lưu DB thất bại.

### P2 — Xóa tài liệu không xóa tệp vật lý

Vị trí: backend/regulations/views.py:76 và models/regulations.py.
Tái hiện: tạo tài liệu với InMemoryStorage, xóa bản ghi, storage.exists vẫn True; transaction đã rollback.
Tệp không còn là nguồn RAG nhưng tiếp tục chiếm dung lượng và giữ nội dung cũ. Xóa quy định qua CASCADE cũng cần chính sách dọn tệp.
Đề xuất: dọn tệp sau transaction commit, kiểm thử xóa tài liệu và xóa quy định. Nếu cần lưu trữ lịch sử thì mô tả rõ thời hạn lưu.

### Tài liệu còn trạng thái cũ

requirements_traceability.md và ai_evidence/synchronization.md vẫn ghi chưa xác nhận khóa/model, trong khi verification.md đã bổ sung kết quả API thật. Cần phân biệt lịch sử và trạng thái hiện tại. Ba vòng đánh giá prompt có nhận xét của nhóm vẫn chưa hoàn thành.

## Giới hạn và triển khai

check --deploy báo 5 cảnh báo: DEBUG, HTTPS redirect, HSTS, secure session cookie, secure CSRF cookie. Phù hợp cấu hình chạy localhost hiện tại, chưa phải cấu hình triển khai công khai.
Chưa kiểm tra trực quan toàn bộ trang trên desktop/mobile trong đợt này; biên dịch template và HTTP tests không thay thế kiểm tra bố cục.
Chưa xác minh tải đồng thời PostgreSQL, phục hồi backup thực tế hoặc chất lượng AI qua ba vòng thực nghiệm. Không tuyên bố dự án không còn lỗi chỉ vì tests đạt.
