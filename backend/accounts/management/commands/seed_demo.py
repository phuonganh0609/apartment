"""Idempotent fictional demo fixtures. Never overwrite existing passwords."""

import os
import secrets
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from buildings.models import Amenity, Apartment, ApartmentAmenity, Building
from contracts.models import Contract
from contracts.services import save_contract
from maintenance.models import MaintenanceRequest
from payments.models import Payment
from regulations.models import Regulation
from tenants.models import Contact, Tenant


class Command(BaseCommand):
    help = "Create fictional demo data and three role accounts (DEBUG only)."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Chỉ tạo dữ liệu demo khi DEBUG=True.")
        password = os.environ.get("DEMO_PASSWORD") or secrets.token_urlsafe(14)
        created_users = []
        for username, full_name, role, deposit in [
            ("quanly", "Quản lý Demo", "manager", True),
            ("nhanvien", "Nhân viên Demo", "staff", False),
            ("ketoan", "Kế toán Demo", "accountant", True),
        ]:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "full_name": full_name,
                    "role": role,
                    "can_edit_deposit": deposit,
                },
            )
            if created:
                user.set_password(password)
                user.save()
                created_users.append(username)
        buildings = []
        for name, address in [
            (
                "An Cư Riverside",
                ("12 đường Ven Sông, Thái Nguyên (dữ l" "iệu demo)"),
            ),
            (
                "An Cư Garden",
                ("28 đường Cây Xanh, Thái Nguyên (dữ l" "iệu demo)"),
            ),
        ]:
            building, _ = Building.objects.get_or_create(
                name=name,
                defaults={
                    "address": address,
                    "description": "Tòa nhà minh họa phục vụ học tập.",
                },
            )
            buildings.append(building)
        amenities = [
            Amenity.objects.get_or_create(name=name)[0]
            for name in ["Điều hòa", "Bình nóng lạnh", "Tủ lạnh", "Máy giặt"]
        ]
        apartments = []
        for index in range(16):
            building = buildings[index // 8]
            apartment, _ = Apartment.objects.get_or_create(
                building=building,
                code=f'{"R" if index < 8 else "G"}{101 + index % 8}',
                defaults={
                    "floor": 1 + index % 4,
                    "area": 35 + index * 3,
                    "rent": 4500000 + index * 250000,
                    "status": "maintenance" if index == 15 else "available",
                },
            )
            apartments.append(apartment)
            for amenity in amenities[: 2 + index % 3]:
                ApartmentAmenity.objects.get_or_create(
                    apartment=apartment,
                    amenity=amenity,
                    defaults={"quantity": 1},
                )
        today = timezone.localdate()
        names = [
            "Minh An",
            "Thu Hà",
            "Hoàng Nam",
            "Mai Linh",
            "Đức Huy",
            "Ngọc Anh",
            "Quang Minh",
            "Phương Thảo",
            "Hải Đăng",
            "Bảo Ngọc",
        ]
        for index, name in enumerate(names):
            tenant, _ = Tenant.objects.get_or_create(
                identity_number=("00000000" f"{index:04d}"),
                defaults={
                    "full_name": name + " (Demo)",
                    "phone": ("090000" f"{index:04d}"),
                    "email": f"tenant{index}@example.com",
                    "address": (
                        "Địa chỉ minh họa, không phải thông t" "in người thật"
                    ),
                },
            )
            Contact.objects.get_or_create(
                tenant=tenant,
                full_name="Người liên hệ Demo",
                defaults={
                    "phone": "0900000099",
                    "relationship": "Người thân",
                    "email": "contact@example.com",
                },
            )
            contract, created = Contract.objects.get_or_create(
                code=f"HD-DEMO-{index + 1:03d}",
                defaults={
                    "apartment": apartments[index],
                    "tenant": tenant,
                    "start_date": today - timedelta(days=120),
                    "end_date": today
                    + timedelta(days=7 + index * 5 if index < 4 else 200),
                    "deposit_amount": apartments[index].rent * 2,
                    "status": "active",
                },
            )
            if created:
                contract.contract_content = (
                    "Hợp đồng "
                    f"{contract.code}"
                    ". Thời hạn từ "
                    f"{contract.start_date:%d/%m/%Y}"
                    " đến "
                    f"{contract.end_date:%d/%m/%Y}"
                    ". Tiền thuê "
                    f"{apartments[index].rent:,.0f}"
                    " đồng/tháng. Tiền cọc "
                    f"{contract.deposit_amount:,.0f}"
                    " đồng. Thanh toán trước ngày 05 mỗi"
                    " tháng. Khi chấm dứt cần thông báo "
                    "trước 30 ngày. Tiền cọc được đối so"
                    "át sau khi hoàn thành nghĩa vụ than"
                    "h toán và bàn giao căn hộ."
                )
                save_contract(contract)
            for month_offset in range(3):
                year = today.year
                month = today.month - month_offset
                while month <= 0:
                    month += 12
                    year -= 1
                due = today.replace(year=year, month=month, day=5)
                paid = month_offset > 0 or index % 3 != 0
                payment, new = Payment.objects.get_or_create(
                    contract=contract,
                    kind="rent",
                    due_date=due,
                    defaults={
                        "amount": apartments[index].rent,
                        "status": "paid" if paid else "pending",
                        "paid_date": min(due, today) if paid else None,
                    },
                )
        for index, content, priority in [
            (1, "Điều hòa phòng ngủ cần kiểm tra", "normal"),
            (5, "Vòi nước bếp bị rò rỉ", "high"),
            (8, "Thay bóng đèn ban công", "low"),
        ]:
            MaintenanceRequest.objects.get_or_create(
                apartment=apartments[index],
                content=content,
                defaults={"priority": priority, "status": "open"},
            )
        for title, content in [
            (
                "Giờ yên tĩnh",
                (
                    "Giờ yên tĩnh từ 22:00 đến 06:00. Khô"
                    "ng mở nhạc lớn, tổ chức tiệc gây ồn "
                    "hoặc thi công trong khung giờ này."
                ),
            ),
            (
                "Quy định thú cưng",
                (
                    "Khách thuê được nuôi thú cưng sau kh"
                    "i đăng ký với quản lý. Thú cưng phải"
                    " được giữ dây khi đi trong khu vực c"
                    "hung. Chủ nuôi chịu trách nhiệm vệ s"
                    "inh."
                ),
            ),
            (
                "Gia hạn và bàn giao",
                (
                    "Khách thuê cần thông báo nhu cầu gia"
                    " hạn ít nhất 30 ngày trước ngày hết "
                    "hạn hợp đồng. Khi bàn giao cần kiểm "
                    "kê tiện ích và đối soát các khoản cò"
                    "n nợ."
                ),
            ),
            (
                "Thanh toán tiền thuê",
                (
                    "Tiền thuê được thanh toán trước ngày"
                    " 05 mỗi tháng theo nội dung hợp đồng"
                    ". Liên hệ kế toán để xác nhận số tiề"
                    "n và nhận thông tin thanh toán."
                ),
            ),
        ]:
            Regulation.objects.get_or_create(
                title=title,
                defaults={"content": content, "document_type": "Nội quy demo"},
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Đã tạo dữ liệu demo. Dữ liệu đã có không bị ghi đè."
            )
        )
        if created_users:
            self.stdout.write("Tài khoản mới: " + ", ".join(created_users))
            self.stdout.write("Mật khẩu demo dùng chung: " + password)
            self.stdout.write(
                (
                    "Lưu mật khẩu này để đăng nhập. Không"
                    " sử dụng các tài khoản demo khi triể"
                    "n khai thật."
                )
            )
