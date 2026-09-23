# Đối chiếu ba tài liệu nguồn

Nguồn: ../ContextProject.txt, ../informember.md, ../project.md. Ngày đồng bộ: 23/09/2026.
Giữ nguyên ba tài liệu đầu vào. Yêu cầu trực tiếp gom sáu thư mục được ưu tiên; Django vẫn chia app và giữ ORM/migrations.

| Nhóm yêu cầu | Vị trí triển khai/minh chứng | Trạng thái |
|---|---|---|
| Thông tin nhóm/trường/khoa | README, technical_report.md | Đồng bộ project.md |
| Django, HTML/CSS/JS, Bootstrap, SQLite | backend, frontend, requirements.txt | Có; PostgreSQL là tùy chọn chưa thử thực tế |
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
