"""Repeatable, fictional rental scenarios at a real geographic location."""

import os
import secrets
from datetime import timedelta

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


def month_date(day, offset, number=1):
    index = day.year * 12 + day.month - 1 + offset
    year, month = divmod(index, 12)
    return day.replace(year=year, month=month + 1, day=number)


class Command(BaseCommand):
    help = 'Create five demo accounts and realistic fictional rental scenarios.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Chỉ tạo demo khi DEBUG=True.')
        today = timezone.localdate()
        password = os.getenv('DEMO_PASSWORD') or secrets.token_urlsafe(14)
        created_users = []
        users = {}
        for username, name, role in [
            ('admin', 'Nguyễn Hoàng Minh', 'manager'),
            ('quanly', 'Trần Thu Hương', 'manager'),
            ('nhanvien', 'Lê Đức Anh', 'staff'),
            ('ketoan', 'Phạm Ngọc Mai', 'accountant'),
            ('khachthue', 'Nguyễn Minh Tuấn', 'tenant'),
        ]:
            user, created = User.objects.get_or_create(username=username, defaults={
                'full_name': name, 'role': role,
                'email': f'{username}@example.com',
                'is_staff': username == 'admin',
                'is_superuser': username == 'admin',
                'can_edit_deposit': role in ('manager', 'accountant'),
            })
            if not created and (user.role != role or
                    (username == 'admin' and not user.is_superuser)):
                raise CommandError(f'Tài khoản {username} đã tồn tại với quyền khác; không ghi đè.')
            if created:
                user.set_password(password)
                user.save()
                created_users.append(username)
            users[username] = user

        buildings = []
        for code in ('S1.01', 'S1.02', 'S1.03'):
            building, _ = Building.objects.get_or_create(
                name=f'Vinhomes Smart City - {code}', defaults={
                    'address': f'Tòa {code}, Vinhomes Smart City, Đại lộ Thăng Long, Tây Mỗ, Hà Nội',
                    'description': 'Địa điểm thực; danh mục căn hộ và giao dịch là dữ liệu demo hư cấu, không phải thông tin chào thuê thực tế.',
                })
            buildings.append(building)
        amenities = [Amenity.objects.get_or_create(name=name)[0] for name in
                     ('Điều hòa', 'Bình nóng lạnh', 'Tủ lạnh', 'Máy giặt', 'Giường ngủ', 'Tủ quần áo', 'Bếp từ')]
        apartments = []
        for index in range(24):
            unit = index % 8
            floor = 5 + unit
            category = unit % 4
            area = (30, 43, 63, 82)[category]
            rent = (6000000, 8000000, 11000000, 14000000)[category]
            apartment, _ = Apartment.objects.get_or_create(
                building=buildings[index // 8], code=f'{floor:02d}{unit % 2 + 1:02d}',
                defaults={'floor': floor, 'area': area, 'rent': rent,
                          'status': 'maintenance' if index == 23 else 'available',
                          'is_listed': 18 <= index < 23,
                          'public_description': f'Căn hộ {("studio", "1 phòng ngủ", "2 phòng ngủ", "3 phòng ngủ")[category]}, {area} m², đủ nội thất. Tin demo phục vụ học tập.',
                          })
            apartments.append(apartment)
            for amenity in amenities:
                ApartmentAmenity.objects.get_or_create(
                    apartment=apartment, amenity=amenity,
                    defaults={'quantity': (max(1, category) if amenity.name in ('Điều hòa', 'Giường ngủ', 'Tủ quần áo') else 1)})

        names = [
            ('Nguyễn Minh Tuấn', 'Nguyễn Văn Thành', 'Bố'),
            ('Trần Thị Lan Anh', 'Trần Thị Hạnh', 'Mẹ'),
            ('Lê Hoàng Nam', 'Lê Hoàng Long', 'Anh trai'),
            ('Phạm Thu Hà', 'Phạm Văn Hùng', 'Bố'),
            ('Hoàng Đức Huy', 'Hoàng Thị Hoa', 'Mẹ'),
            ('Vũ Ngọc Linh', 'Vũ Minh Quân', 'Anh trai'),
            ('Đặng Quang Minh', 'Đặng Văn Hải', 'Bố'),
            ('Bùi Phương Thảo', 'Bùi Thị Hồng', 'Mẹ'),
            ('Đỗ Hải Đăng', 'Đỗ Thu Trang', 'Chị gái'),
            ('Ngô Bảo Ngọc', 'Ngô Văn Sơn', 'Bố'),
            ('Dương Anh Khoa', 'Dương Thị Liên', 'Mẹ'),
            ('Đinh Khánh Chi', 'Đinh Quang Vinh', 'Anh trai'),
            ('Hồ Gia Bảo', 'Hồ Văn Phúc', 'Bố'),
            ('Phan Thanh Tâm', 'Phan Thị Hòa', 'Mẹ'),
            ('Nguyễn Thùy Dương', 'Nguyễn Đức Dũng', 'Anh trai'),
            ('Trần Quốc Việt', 'Trần Văn Bình', 'Bố'),
            ('Lê Mỹ Linh', 'Lê Thị Nguyệt', 'Mẹ'),
            ('Phạm Tiến Đạt', 'Phạm Minh Đức', 'Anh trai'),
        ]
        contracts = []
        for index, (name, contact_name, relationship) in enumerate(names):
            # Deliberately synthetic identity/contact numbers; never scraped personal data.
            tenant, _ = Tenant.objects.get_or_create(
                identity_number=f'000099{index + 1:06d}', defaults={
                    'full_name': name, 'phone': f'000099{index + 1:04d}',
                    'email': f'cu-dan-{index + 1:02d}@example.com',
                    'address': ('Đường Nguyễn Trãi, Thanh Xuân, Hà Nội',
                                'Đường Cầu Giấy, Cầu Giấy, Hà Nội',
                                'Đường Lê Văn Lương, Thanh Xuân, Hà Nội')[index % 3],
                })
            Contact.objects.get_or_create(tenant=tenant, full_name=contact_name,
                defaults={'relationship': relationship, 'phone': f'000088{index + 1:04d}',
                          'email': f'lien-he-{index + 1:02d}@example.com'})
            if index == 0:
                user = users['khachthue']
                if user.tenant_id and user.tenant_id != tenant.pk:
                    raise CommandError('khachthue đã liên kết hồ sơ khác; không ghi đè.')
                user.tenant = tenant
                user.save(update_fields=['tenant'])
            start = month_date(today, -5)
            end = month_date(today, 7) - timedelta(days=1)
            status, deposit_status = 'active', 'collected'
            if index < 3:
                end = today + timedelta(days=(7, 15, 25)[index])
            elif index == 16:
                start = month_date(today, -12)
                end = month_date(today, -1) - timedelta(days=1)
                status, deposit_status = 'terminated', 'refunded'
            elif index == 17:
                start = month_date(today, 1)
                end = month_date(today, 13) - timedelta(days=1)
                status, deposit_status = 'draft', 'pending'
            apartment = apartments[index]
            contract, created = Contract.objects.get_or_create(
                code=f'HD-NESTORA-{index + 1:03d}', defaults={
                    'tenant': tenant, 'apartment': apartment, 'start_date': start,
                    'end_date': end, 'status': status,
                    'deposit_amount': apartment.rent * 2, 'deposit_status': deposit_status,
                })
            if created:
                contract.contract_content = (
                    f'Hợp đồng demo {contract.code}. Bên thuê: {tenant.full_name}. '
                    f'Căn hộ {apartment}, diện tích {apartment.area} m². '
                    f'Thời hạn {start:%d/%m/%Y} đến {end:%d/%m/%Y}. '
                    f'Giá thuê {apartment.rent:,.0f} đồng/tháng; cọc {contract.deposit_amount:,.0f} đồng (2 tháng). '
                    f'Phí quản lý demo {int(apartment.area) * 12000:,} đồng/tháng, tính 12.000 đồng/m². '
                    'Thanh toán hàng tháng, hạn ngày 05. Điện nước và gửi xe thanh toán riêng theo hóa đơn thực tế. '
                    'Báo trước 30 ngày khi không gia hạn. Không tự ý cải tạo; giữ yên tĩnh từ 22h đến 6h. '
                    'Đối soát công nợ và hư hỏng khi bàn giao, hoàn cọc trong 7 ngày làm việc sau đối soát. '
                    'Tên và giao dịch hư cấu phục vụ học tập; không phải hợp đồng của cư dân thực tế.'
                )
                if status == 'terminated':
                    contract.full_clean()
                    contract.save()
                else:
                    save_contract(contract)
                contract.ai_authorized_users.add(users['quanly'], users['nhanvien'], users['ketoan'])
            contracts.append(contract)
            if contract.status == 'draft':
                continue
            for offset in range(-5, 1):
                due = month_date(today, offset, 5)
                if not contract.start_date <= due <= min(contract.end_date, today):
                    continue
                paid = not (contract.status == 'active' and offset == 0 and index % 4 == 0)
                for kind, amount in [('rent', apartment.rent), ('service', int(apartment.area) * 12000)]:
                    payment, _ = Payment.objects.get_or_create(
                        contract=contract, kind=kind, due_date=due,
                        defaults={'amount': amount, 'status': 'paid' if paid else 'pending',
                                  'paid_date': due - timedelta(days=1) if paid else None})
                    payment.full_clean()

        for index, content, priority, state, notes in [
            (0, 'Điều hòa phòng khách không mát', 'normal', 'open', 'Chờ kỹ thuật kiểm tra bộ lọc và gas.'),
            (4, 'Rò nước dưới chậu rửa bếp', 'high', 'processing', 'Đã khóa van cục bộ, hẹn thay dây cấp nước.'),
            (8, 'Đèn ban công nhấp nháy', 'low', 'done', 'Đã thay bóng LED và kiểm tra nguồn điện.'),
            (12, 'Bình nóng lạnh không làm nóng', 'normal', 'processing', 'Đã ngắt điện thiết bị, chờ linh kiện thay thế.'),
            (23, 'Kiểm tra điện nước và sơn lại căn hộ trước bàn giao', 'normal', 'processing', 'Tạm ngừng cho thuê đến khi nghiệm thu.'),
        ]:
            MaintenanceRequest.objects.get_or_create(apartment=apartments[index], content=content,
                defaults={'priority': priority, 'status': state, 'notes': notes,
                          'submitted_by': users['khachthue'] if index == 0 else users['nhanvien']})
        for title, audience, content in [
            ('Nội quy cư dân Nestora', 'tenants', 'Giữ yên tĩnh 22h–6h. Đăng ký khách qua đêm với quản lý. Không để vật dụng chắn lối thoát hiểm. Thú cưng phải đăng ký và đeo dây tại khu vực chung.'),
            ('Biểu phí và kỳ thanh toán Nestora', 'tenants', 'Biểu phí demo: phí quản lý 12.000 đồng/m²/tháng; cọc 2 tháng tiền thuê; tiền thuê và phí quản lý đến hạn ngày 05. Điện, nước, gửi xe theo hóa đơn riêng, không bao gồm trong giá thuê.'),
            ('Quy trình đối soát và hoàn cọc Nestora', 'finance', 'Kiểm tra tiền thuê, phí còn nợ và biên bản bàn giao. Hoàn cọc trong 7 ngày làm việc sau đối soát. Không tính tiền cọc vào doanh thu thuê.'),
            ('Hướng dẫn đăng ký thuê Nestora', 'public', 'Danh mục và mức giá trên hệ thống này là dữ liệu demo. Liên hệ quản lý để xem căn, kiểm tra tình trạng và thống nhất hợp đồng trước khi thanh toán.'),
        ]:
            Regulation.objects.get_or_create(title=title, defaults={
                'audience': audience, 'content': content, 'document_type': 'Quy định demo'})
        self.stdout.write(self.style.SUCCESS('Đã tạo demo; không ghi đè dữ liệu hoặc mật khẩu đã tồn tại.'))
        if created_users:
            self.stdout.write('Tài khoản mới: ' + ', '.join(created_users))
            self.stdout.write('Mật khẩu demo: ' + password)
