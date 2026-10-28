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
