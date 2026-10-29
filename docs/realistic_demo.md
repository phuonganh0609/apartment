# Dữ liệu demo Nestora

Tạo hoặc bổ sung dữ liệu bằng:

```powershell
.venv/Scripts/python.exe -X utf8 manage.py seed_realistic_demo
```

Lệnh chỉ chạy khi `DEBUG=True`, dùng transaction, giữ dữ liệu và mật khẩu đã có.
Mật khẩu ngẫu nhiên chỉ in khi tạo tài khoản mới; không lưu trong mã nguồn.
Tài khoản `admin` có quyền Django Admin; `quanly`, `nhanvien`, `ketoan` có
vai trò nghiệp vụ tương ứng. `khachthue` liên kết hồ sơ Nguyễn Minh Tuấn
và hợp đồng HD-NESTORA-001. Nhân sự được phân công AI trên các hợp đồng demo.

Tạo 3 tòa, 24 căn, 18 khách thuê cùng người liên hệ; 16 hợp đồng đang thuê,
1 đã thanh lý, 1 bản nháp; khoản thu tiền thuê và phí quản lý trong tối đa
6 tháng gần đây; 5 yêu cầu bảo trì. Các ngày tính theo ngày chạy lần đầu.
Chạy lại không dịch chuyển hợp đồng hay đặt lại trạng thái thanh toán.
Không tạo khoản thu trước thời hạn hợp đồng, sau ngày kết thúc hoặc cho bản nháp.
Khoản đã thu có ngày thu không nằm trong tương lai. Cọc bằng 2 tháng tiền thuê;
hợp đồng thanh lý đã hoàn cọc và không có công nợ. Ba hợp đồng sắp hết hạn
trong 7, 15 và 25 ngày; bốn hợp đồng có công nợ kỳ hiện tại (khi qua ngày 05).

Địa điểm Vinhomes Smart City, Đại lộ Thăng Long, Tây Mỗ, Hà Nội là có thật:
https://smartcity.vinhomes.vn/

Giá demo studio 30 m²: 6 triệu; 1 phòng ngủ 43 m²: 8 triệu;
2 phòng ngủ 63 m²: 11 triệu; 3 phòng ngủ 82 m²: 14 triệu đồng/tháng.
Tham khảo mặt bằng chào thuê, không phải định giá hay xác nhận tin còn hiệu lực:
https://duanvinhomes.vn/tin-tuc/thue-vinhomes-smart-city/

Phí quản lý 12.000 đồng/m²/tháng là giả định của bộ demo, không phải biểu phí
chính thức của dự án. Điện, nước, gửi xe không được đưa vào khoản thu mẫu.
Tên Việt Nam được ghép cho nhân vật hư cấu; không xác nhận họ là cư dân thực.
CCCD bắt đầu `000099`, điện thoại bắt đầu `0000` và email `example.com` là
dữ liệu giả để không gán giao dịch tài chính cho người thật. Địa chỉ thường trú
chỉ dùng tên đường có thật, không gán số nhà của một hộ dân cụ thể.
