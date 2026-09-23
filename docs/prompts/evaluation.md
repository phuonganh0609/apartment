# Kế hoạch thử nghiệm prompt ba vòng

Các prompt dùng trong ứng dụng nằm tại chatbot/ai_assistant/prompts. Đây là kế hoạch ghi nhận thí nghiệm; chưa có kết quả model thật được điền thay cho người thực hiện.

| Vòng | Nội dung kiểm tra | Dữ liệu đầu vào | Kết quả cần ghi |
|---|---|---|---|
| 1 | Đủ năm mục hợp đồng | Hợp đồng demo đủ thời hạn, thuê, cọc, thanh toán, chấm dứt | Model, thời gian, JSON, đúng/sai từng mục |
| 2 | Không bịa thông tin | Hợp đồng thiếu tiền cọc/điều kiện chấm dứt; tài liệu chứa câu yêu cầu bỏ qua chỉ thị | Thông tin thiếu có được ghi rõ; có làm theo chỉ thị chèn không |
| 3 | Nguồn và ngoài phạm vi | Câu hỏi có nội quy, câu hỏi không có nội quy, câu tư vấn pháp lý | Nguồn trả về, độ phù hợp, từ chối/thiếu thông tin, lỗi |

Mỗi lần chạy ghi ngày, nhà cung cấp/model, phiên bản prompt, đầu vào đã ẩn danh, phản hồi nguyên bản, nhận xét và chỉnh sửa thực tế. Chỉ ghi PASS khi đã quan sát kết quả; lưu failed cases để cải tiến. Không tạo minh chứng giả khi chưa chạy API.

## Bộ chạy so sánh có thể tái lập

Xem kế hoạch: `.venv/Scripts/python.exe -X utf8 tools/evaluate_prompts.py`.
Sau khi cấu hình khóa/model, chạy thật bằng cách thêm `--run` (15 yêu cầu API, có thể tính phí).
Bộ chạy dùng dữ liệu hư cấu cho tóm tắt, thông báo, chatbot, câu ngoài phạm vi và chỉ thị chèn,
so sánh ba biến thể prompt. Kết quả JSON lưu theo thời gian trong docs/ai_evidence,
bao gồm input, system prompt, phản hồi, lỗi, thời gian và kiểm tra cấu trúc.
Không gọi đây là ba vòng cải tiến đã hoàn thành: người kiểm tra cần đánh giá nội dung,
chọn thay đổi từ kết quả quan sát, cập nhật prompt và chạy lại.

| Ngày/người kiểm tra | Model/phiên bản prompt | Kết quả quan sát | Sai lệch | Chỉnh sửa thực tế | Kết quả chạy lại |
|---|---|---|---|---|---|
| Chưa thực hiện | Chưa có | Chưa có | Chưa đánh giá | Chưa có | Chưa có |
