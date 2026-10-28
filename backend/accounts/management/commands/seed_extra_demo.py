"""Additional fictional demo records; safe to rerun without overwriting."""
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from accounts.models import User
from buildings.models import Building, Apartment, Amenity, ApartmentAmenity
from tenants.models import Tenant, Contact
from contracts.models import Contract
from contracts.services import save_contract
from payments.models import Payment
from maintenance.models import MaintenanceRequest
from regulations.models import Regulation

class Command(BaseCommand):
    help = "Add fictional public listings and complete operational demo scenarios."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Chỉ tạo demo khi DEBUG=True.")
        today = timezone.localdate()
        building, _ = Building.objects.get_or_create(name="Nestora Demo Central", defaults={
            "address": "Khu trung tâm minh họa, Thái Nguyên (địa chỉ giả lập)",
            "description": "Tòa nhà demo bổ sung phục vụ học tập.",
        })
        amenities = [Amenity.objects.get_or_create(name=name)[0] for name in ("Điều hòa", "Tủ lạnh", "Máy giặt", "Internet demo")]
        for i in range(12):
            apartment, _ = Apartment.objects.get_or_create(building=building, code=f"DEMO-C{i+1:03}", defaults={
                "floor": 1+i//4, "area": 32+i*4, "rent": 3500000+i*350000,
                "is_listed": i>=6 and i<11,
                "status": "maintenance" if i==11 else "available",
                "public_description": "Căn hộ demo hư cấu, không phải tin cho thuê thực tế. Không gian minh họa có bếp, khu sinh hoạt và tiện ích cơ bản.",
            })
            for amenity in amenities:
                ApartmentAmenity.objects.get_or_create(apartment=apartment, amenity=amenity, defaults={"quantity":1})
            if i>=6:
                continue
            tenant, _ = Tenant.objects.get_or_create(identity_number=f"990000000{i+1:03}", defaults={
                "full_name": f"Khách mẫu bổ sung {i+1} (Demo)", "phone": f"09099900{i+1:02}",
                "email": f"demo-customer-{i+1}@example.com", "address": "Địa chỉ hư cấu phục vụ kiểm thử",
            })
            Contact.objects.get_or_create(tenant=tenant, full_name=f"Liên hệ mẫu {i+1}", defaults={"relationship":"Người thân demo", "phone":"0909990099"})
            account, new = User.objects.get_or_create(username=f"khach_demo{i+1}", defaults={
                "full_name":tenant.full_name, "email":tenant.email, "role":"tenant", "tenant":tenant,
            })
            if new:
                account.set_password("Demo@2026"); account.save()
            contract, new = Contract.objects.get_or_create(code=f"HD-EXTRA-DEMO-{i+1:03}", defaults={
                "apartment":apartment, "tenant":tenant, "start_date":today-timedelta(days=90),
                "end_date":today+timedelta(days=10+i*30), "status":"active",
                "deposit_amount":apartment.rent*2, "deposit_status":"collected" if i%2==0 else "pending",
                "contract_content":f"Hợp đồng demo hư cấu. Thuê căn {apartment.code}, tiền thuê {apartment.rent} đồng/tháng, cọc {apartment.rent*2} đồng. Thanh toán trước ngày 05 mỗi tháng. Gia hạn báo trước 30 ngày. Hoàn cọc sau khi bàn giao và đối soát nghĩa vụ thanh toán. Thời hạn đến {(today+timedelta(days=10+i*30)):%d/%m/%Y}.",
            })
            if new:
                save_contract(contract)
            for kind, amount in (("rent",apartment.rent),("service",350000)):
                for offset, paid in ((-35,True),(-5,False),(3+i,False)):
                    due = today+timedelta(days=offset)
                    Payment.objects.get_or_create(contract=contract,kind=kind,due_date=due,defaults={
                        "amount":amount,"status":"paid" if paid else "pending","paid_date":due if paid else None,
                    })
            MaintenanceRequest.objects.get_or_create(apartment=apartment,content=f"Yêu cầu demo {i+1}: kiểm tra thiết bị căn hộ",defaults={
                "submitted_by":account,"priority":"high" if i==0 else "normal",
                "status":("open","processing","done")[i%3],
                "notes":"Nhân viên đã tiếp nhận, đang lên lịch kiểm tra." if i%3==1 else "Đã xử lý (demo)." if i%3==2 else "",
            })
        for title, audience, content in (
            ("Demo · Tham quan căn hộ", "public", "Liên hệ ban quản lý để xác nhận lịch tham quan. Đây là quy định giả lập phục vụ demo."),
            ("Demo · Thông tin giá thuê", "public", "Giá hiển thị là giá tham khảo theo tháng. Phí dịch vụ và tiền cọc cần xác nhận với ban quản lý. Dữ liệu hư cấu."),
            ("Demo · Quy định hoàn cọc", "tenants", "Tiền cọc được hoàn sau khi kiểm tra tình trạng căn hộ, bàn giao và đối chiếu các khoản phải thanh toán theo hợp đồng. Liên hệ quản lý để xác nhận thời điểm cụ thể. Quy định demo hư cấu."),
            ("Demo · Báo hỏng và bảo trì", "tenants", "Đăng nhập, mở mục Báo hỏng, chọn căn hộ đang thuê và mô tả sự cố. Theo dõi trạng thái và phản hồi trong yêu cầu của tôi. Nội dung demo."),
            ("Demo · Phí dịch vụ", "finance", "Phí dịch vụ demo 350.000 đồng/tháng được theo dõi riêng với tiền thuê. Kế toán đối soát trước khi xác nhận đã thu."),
            ("Demo · Xử lý bảo trì nội bộ", "internal", "Nhân viên tiếp nhận yêu cầu, kiểm tra mức độ ưu tiên, cập nhật đang xử lý và ghi phản hồi trước khi đánh dấu hoàn thành."),
        ):
            Regulation.objects.get_or_create(title=title,defaults={"content":content,"audience":audience,"document_type":"Demo bổ sung","is_active":True})
        self.stdout.write(self.style.SUCCESS("Demo bổ sung đã sẵn sàng. Có thể chạy lại, không ghi đè dữ liệu cũ."))
        self.stdout.write("Tài khoản mới (nếu vừa tạo): khach_demo1 đến khach_demo6; mật khẩu Demo@2026. Chỉ dùng localhost.")
