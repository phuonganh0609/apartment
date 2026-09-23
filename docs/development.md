# Phát triển và quản lý phiên bản

Cài công cụ: `.venv/Scripts/python.exe -m pip install -r requirements-dev.txt`.
Định dạng: `.venv/Scripts/python.exe -m black backend chatbot models RAG tools`.
Kiểm tra style: `.venv/Scripts/python.exe -m pycodestyle backend chatbot models RAG tools`. Bỏ E203/W503 để dùng cách định dạng slice và xuống dòng trước toán tử của Black; giới hạn dòng vẫn là 79 ký tự.

Chạy check, makemigrations --check --dry-run và test tests trước khi commit.

Git lưu mã nguồn và tài liệu; .gitignore loại .env, SQLite, media, .venv, staticfiles và cache.
Không đưa khóa/tài liệu riêng tư vào commit. Kiểm tra `git status` và `git diff` trước khi thêm file.
Tác giả cấu hình user.name/user.email bằng danh tính thật của mình, rồi commit từng nhóm thay đổi với nội dung rõ ràng. Không dựng lại các commit lịch sử chưa từng có.

Các ghi nhận thử nghiệm phải tách test mock và kết quả API thật. Xem requirements_traceability.md để biết điều kiện còn thiếu.
