# Dữ liệu

`db.sqlite3` là cơ sở dữ liệu đang dùng. `media/` chứa tài liệu riêng tư. Lệnh backup_database tạo bản sao trong `backups/`. Không đưa dữ liệu riêng tư lên Git.

## Đồng bộ dữ liệu demo

`demo_snapshot.json` lưu dữ liệu demo hư cấu cùng 3 tài khoản tạo ngày 08/09/2026: `quanly`, `nhanvien`, `ketoan`. Mật khẩu chung là `Demo@2026`, được lưu dưới dạng băm trong tệp. Tệp không chứa phiên đăng nhập, khóa API hoặc tài liệu đính kèm.

Sau khi pull mã nguồn, dừng server rồi chạy tại thư mục dự án:

```powershell
.venv/Scripts/python.exe -X utf8 manage.py backup_database
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py loaddata data/demo_snapshot.json
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000
```

Với máy mới chưa có cơ sở dữ liệu, bỏ qua lệnh sao lưu. Lệnh nhập sẽ ghi đè các bản ghi có cùng ID; các bản ghi bổ sung trên máy nhận vẫn được giữ lại. Chỉ dùng snapshot này cho môi trường demo.
