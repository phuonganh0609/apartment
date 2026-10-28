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

# Đối chiếu ba tài liệu nguồn

Nguồn: requirements/ContextProject.txt, requirements/informember.md, requirements/project.md. Ngày đồng bộ: 23/09/2026.
Giữ nguyên ba tài liệu đầu vào. Yêu cầu trực tiếp gom sáu thư mục được ưu tiên; Django vẫn chia app và giữ ORM/migrations.

| Nhóm yêu cầu | Vị trí triển khai/minh chứng | Trạng thái |
|---|---|---|
| Thông tin nhóm/trường/khoa | README, technical_report.md | Đồng bộ requirements/project.md |
| Django, HTML/CSS/JS, Bootstrap, SQLite | backend, frontend, requirements/base.txt | Có; PostgreSQL là tùy chọn chưa thử thực tế |
| Google Gemini API | chatbot/ai_assistant/services/ai_client.py; .env.example | Có adapter và test mock; cần GEMINI_API_KEY và AI_MODEL để chạy thật |
| Vai trò/xác thực/CSRF | backend/accounts, backend/config/settings.py | Có; tests test_auth/test_pages |
| Danh mục căn/tòa/tiện ích, khách/liên hệ | backend/buildings, backend/tenants, models | Có CRUD/tìm kiếm và ràng buộc |
| Hợp đồng/cọc/lịch/gia hạn/thanh lý | backend/contracts, models/contracts.py | Có; test_contracts |
| Thuê/phí/công nợ | backend/payments, models/payments.py | Có; test_payments |
| Bảo trì/cảnh báo/báo cáo | backend/maintenance, alerts, reports | Có; test_alerts/test_pages và checklist thủ công |
| AI tóm tắt/soạn nháp/chatbot | chatbot/ai_assistant, RAG | Có luồng; chưa xác nhận chất lượng Gemini thật |
| Use case, ERD, I/O, phi chức năng | technical_report.md, diagrams/architecture.md | Đã mô tả; cần nhóm duyệt |
| Bảo mật và xử lý lỗi AI | adapter, prompt, views, backend/tests/test_ai.py | Kiểm tra mock; cần đánh giá model thật |
| Ba vòng thử prompt (KT3.4) | prompts/evaluation.md, tools/evaluate_prompts.py | Có bộ chạy/mẫu ghi; chưa có kết quả API thật |
| Nhật ký AI/kiểm chứng sinh viên | ai_evidence/implementation.md, synchronization.md | Có lịch sử công việc; nhóm chưa xác nhận |
| README/cấu hình/sao lưu/triển khai | README, .env.example, tools, backup_database | Có hướng dẫn; chưa xác minh production |
| Quản lý Git/commit | development.md | Đã khởi tạo Git cục bộ; mốc đồng bộ mới, không dựng lịch sử trước đó |
| Báo cáo và thuyết trình | technical_report.md, manual_test.md | Báo cáo hiện trạng có; cần kết quả thực nghiệm, ảnh và demo thật |

Không bắt buộc đổi tên app theo tên ví dụ, tạo bảng Deposit, gửi email tự động, vector database, React hoặc Docker. Những mục này không phải điều kiện bắt buộc trong ba tài liệu.
