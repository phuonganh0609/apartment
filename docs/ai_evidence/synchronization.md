# Nhật ký đồng bộ yêu cầu — 23/09/2026

## Yêu cầu thực tế

Người dùng bổ sung ../requirements/ContextProject.txt, ../requirements/project.md, ../requirements/informember.md, yêu cầu kiểm tra độ đồng bộ rồi yêu cầu: “đồng bộ lại theo 3 file tôi mới cho vào”.

## Phân tích và thay đổi do AI hỗ trợ

Đối chiếu cho thấy Context chọn Gemini trong khi adapter cũ chỉ có OpenAI/Ollama, cấu hình thiếu model. Minh chứng ba vòng mới là kế hoạch; tài liệu chứa đường dẫn trước khi gom thư mục. Tên nhóm/lớp đúng nhưng thiếu vai trò và trường/khoa.

Đã thêm adapter Gemini REST, biến GEMINI_API_KEY riêng, dùng adapter chung cho kiểm tra kết nối, bổ sung test giao thức/lỗi, cập nhật README/cấu hình/sơ đồ, báo cáo use case và ma trận yêu cầu. Không gửi khóa OpenAI sẵn có sang Google. Giữ ba tệp nguồn nguyên trạng và giữ migrations/dữ liệu.

## Nguồn kiểm chứng kỹ thuật

- https://ai.google.dev/api/generate-content
- https://ai.google.dev/gemini-api/docs/models

Kiểm thử MockTransport kiểm tra cấu trúc HTTP/JSON và lỗi; không gọi model. Kết quả kiểm thử thực tế được ghi trong ../verification.md sau khi chạy.

## Chưa thực hiện hoặc chưa được nhóm xác nhận

Chưa có khóa/model Gemini được xác nhận, chưa có kết quả ba vòng AI thật, chưa có đánh giá/ảnh demo của sinh viên hay xác minh production. Nhóm bổ sung ngày, người kiểm tra, prompt/phản hồi thực tế và phần đã chỉnh sửa sau mỗi vòng. Không ký thay hoặc tự nhận nhóm đã kiểm chứng.
