## Trạng thái hiện hành — 27/10/2026

- Phạm vi: commit nền `9dc478b` cùng các sửa đổi cục bộ chưa commit trong lần sửa này.
- Đã chạy lại: **65/65 tests đạt** (16,058 giây), Django check không lỗi, migration dry-run không có thay đổi; check_source PASS với 138 file Python.
- Dùng Python 3.12.14 trong `.venv`, Django 5.2.18. Không cần cài Python toàn máy để chạy lại bằng `.venv/Scripts/python.exe`.
- RAG: bỏ từ thời gian phổ biến, yêu cầu ít nhất hai từ khớp cho truy vấn nhiều từ và tỷ lệ khớp >= 0.5. Test câu cổ phiếu, thời tiết, kiện tụng không lấy nguồn; câu nội quy có/không dấu vẫn lấy được nguồn. Đây là cải thiện retrieval từ khóa, chưa bảo đảm hiểu ngữ nghĩa mọi câu hỏi.
- Upload: xử lý lỗi lưu trữ/CSDL, rollback bản ghi và dọn tệp đã ghi khi INSERT thất bại.
- Xóa: dọn tệp sau commit qua signal, áp dụng cả cascade; rollback giữ nguyên tệp. Nếu storage không cho xóa, ghi log để vận hành xử lý, không giả định tệp đã được dọn thành công.
- **AI thật hiện chưa xác minh**: không có `.env` được cung cấp tại checkout này; bộ chạy đánh giá báo thiếu cấu hình khóa/model. Không có yêu cầu API thật được gửi trong lần này.
- **KT3.4 chưa hoàn thành**: cần cấu hình Gemini và chạy/đánh giá ít nhất ba vòng thật. Kết quả so sánh tự động vẫn cần nhận xét và cải tiến dựa trên quan sát; không thay thế xác nhận của sinh viên.
- Ghi nhận Gemini PASS ngày 23/09 bên dưới là lịch sử được lưu trong repo, không có bản ghi phản hồi/mã phiên bản đủ để tái xác minh trên checkout hiện tại.
- Bộ chạy prompt nay lưu commit nền, trạng thái thay đổi cục bộ và SHA-256 prompt để gắn kết quả tương lai với nguồn chạy.
- Chưa kiểm tra trực quan toàn bộ giao diện, production, tải đồng thời hoặc phục hồi backup. Cảnh báo thiếu `frontend/staticfiles/` khi chạy test do chưa collectstatic, không làm test thất bại.

Các nội dung bên dưới phản ánh mốc lịch sử hoặc kế hoạch; khi khác nhau, dùng trạng thái hiện hành ở trên.

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
