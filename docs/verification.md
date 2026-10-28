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

# Trạng thái xác minh

## Kiểm tra bản ban đầu (lịch sử)

- Chạy `tools/check_source.py`: kiểm tra cú pháp Python, sự tồn tại 10 app, đúng 12 domain model và CSRF trong form POST.
- Kết quả kiểm tra tĩnh: PASS.
- Đã cài requirements vào .venv và tải Bootstrap 5.3.8 về frontend/static/vendor.
- Đã tạo và chạy 7 initial migrations của các app nghiệp vụ.
- `manage.py check`: không phát hiện vấn đề.
- `manage.py makemigrations --check --dry-run`: không có thay đổi còn thiếu migration.
- `manage.py test tests --verbosity 1`: 54 test đạt, 0 lỗi (17,578 giây). Test upload được chạy ngoài sandbox vì cần tạo tệp tạm.
- Đã tạo dữ liệu demo: 2 tòa nhà, 16 căn hộ, 10 khách thuê/hợp đồng, 30 khoản thanh toán, 3 yêu cầu bảo trì, 4 quy định, 3 tài khoản vai trò.
- Đã mở ứng dụng tại http://127.0.0.1:8000, đăng nhập quanly và kiểm tra trực quan dashboard trên trình duyệt.
- Định dạng tiền tiếng Việt đã kiểm tra: 33750000 hiển thị 33.750.000.

## Chưa xác nhận

- Gọi API AI thực tế: chưa có cấu hình Gemini đầy đủ và kết quả kiểm tra model thật. Các test AI được thiết kế sử dụng mock; không coi mock là kết quả gọi API thực tế.
- Chưa kiểm tra triển khai production, nhiều người ghi đồng thời trên PostgreSQL hoặc toàn bộ checklist thủ công.

Kết quả trên xác nhận bản demo cục bộ và các luồng trong bộ test; không thay thế đánh giá chất lượng model AI thật.

## Đồng bộ ba tài liệu nguồn — 23/09/2026

- Django system check: không có lỗi; migration dry-run: không phát sinh thay đổi schema.
- Toàn bộ 59 tests đạt sau khi thêm Gemini và định dạng mã nguồn (12,482 giây).
- Sau khi bổ sung trường hợp JSON sai kiểu, chạy lại riêng 20 tests AI: đạt (3,416 giây).
- Black định dạng giới hạn 79 ký tự; pycodestyle đạt với E203/W503 bỏ qua để tương thích Black.
- check_source.py: PASS, 135 file Python, 10 app, 12 model, CSRF trong form POST.
- Bộ chạy evaluate_prompts.py đã kiểm tra chế độ kế hoạch, không gọi API.
- check_ai_connection.py báo thiếu cấu hình, trả exit code 1 như thiết kế.
- Chưa có GEMINI_API_KEY và AI_MODEL hợp lệ được xác nhận; chưa chạy thử nghiệm Gemini thật.
- Đã khởi tạo Git cục bộ; commit đồng bộ là mốc mới, không phải lịch sử phát triển trước đây.

Không coi tests mock, tài liệu vừa bổ sung hay bộ chạy thí nghiệm là minh chứng chất lượng AI thật.

## Kiểm tra kết nối thật sau cấu hình Gemini — 23/09/2026

- Model gemini-3.8-flash trả HTTP 503 quá tải trong lần chẩn đoán.
- Đổi sang gemini-3.5-flash-lite; check_ai_connection.py: PASS.
- Thử ba lời gọi thật bằng dữ liệu hư cấu: tóm tắt đủ 5 mục, thông báo có subject/body, chatbot trả câu trả lời và nguồn: PASS. Nguồn chatbot trong lần này được cấp bằng fixture, không phải kiểm thử truy xuất RAG thực tế.
- Đã khởi động lại Django để nạp .env mới.
- Đây là smoke test, chưa thay thế ba vòng đánh giá chất lượng prompt và kiểm chứng của nhóm. Các ghi nhận thiếu cấu hình phía trên là lịch sử trước khi người dùng điền khóa/model.
