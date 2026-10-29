"""Read-only, bounded ORM lookups. Never execute SQL or filters supplied by AI."""

import re
import unicodedata
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from accounts.permissions import allowed, ALL, FINANCE, OPERATIONS
from buildings.models import ApartmentAmenity
from buildings.services import apartments_with_occupancy
from contracts.models import Contract
from maintenance.models import MaintenanceRequest
from payments.models import Payment

LIMIT = 10


def normalize(text):
    folded = ''.join(c for c in unicodedata.normalize('NFD', text.lower().replace('đ', 'd'))
                     if unicodedata.category(c) != 'Mn')
    return ' '.join(folded.split())


def money(value):
    return f'{value:,.0f}'.replace(',', '.') + ' đồng'


def response(title, lines):
    stamp = timezone.localtime().strftime('%d/%m/%Y %H:%M')
    text = '\n'.join(lines)
    return {'answer': text, 'sources': [{
        'id': 1, 'title': f'Dữ liệu hệ thống · {title} · {stamp}',
        'text': f'Tra cứu trực tiếp lúc {stamp}, theo quyền tài khoản đang đăng nhập.\n{text}',
    }]}


def scope_contracts(user):
    if user.role == 'tenant' and not user.is_superuser:
        return Contract.objects.filter(tenant_id=user.tenant_id) if user.tenant_id else Contract.objects.none()
    return Contract.objects.all() if allowed(user, ALL) else Contract.objects.none()


def narrow_contracts(qs, text):
    code = re.search(r'\bhd-[a-z0-9]+(?:-[a-z0-9]+)*\b', text)
    if code:
        qs = qs.filter(code__iexact=code.group())
    building = re.search(r'\bs\d+\.\d+\b', text)
    if building:
        qs = qs.filter(apartment__building__name__icontains=building.group())
    unit = re.search(r'\b(?:can(?: ho)?|phong)\s+([a-z]?\d{3,6})\b', text)
    if unit:
        qs = qs.filter(apartment__code__iexact=unit.group(1))
    return qs


def answer_system_question(question, user):
    if not user or not user.is_authenticated or not user.is_active:
        return None
    text = normalize(question)
    own = any(s in text for s in ('cua toi', 'toi con', 'toi dang', 'toi co', 'minh con', 'cua minh'))
    code = bool(re.search(r'\bhd-[a-z0-9]+', text))
    # Leave procedural/policy questions to document retrieval.
    policy = any(s in text for s in ('quy dinh', 'quy trinh', 'lam sao', 'cach ', 'bao truoc', 'hoan coc trong'))
    intent = None
    if not policy and any(s in text for s in ('bao tri', 'bao hong', 'sua chua')) and (own or any(s in text for s in ('tien do', 'trang thai', 'xu ly den dau', 'danh sach'))):
        intent = 'maintenance'
    elif not policy and any(s in text for s in ('con no', 'cong no', 'chua thanh toan', 'khoan thu', 'qua han', 'da thanh toan', 'phai thanh toan', 'tien no')):
        intent = 'payments'
    elif not policy and any(s in text for s in ('hop dong', 'het han', 'tien coc')) and (own or code or 'sap het han' in text or 'danh sach hop dong' in text):
        intent = 'contracts'
    elif 'tien ich' in text and ('toa' in text or 'can ho' in text):
        intent = 'amenities'
    elif any(s in text for s in ('con trong', 'can trong', 'con can', 'chua thue', 'dang cho thue', 'gia duoi', 'gia tu', 'duoi ')) and ('can' in text or 'phong' in text):
        intent = 'apartments'
    if intent is None:
        return None
    if not allowed(user, (*ALL, 'tenant')):
        return {'answer': 'Tài khoản không có quyền tra cứu dữ liệu này.', 'sources': []}
    tenant = user.role == 'tenant' and not user.is_superuser
    contracts = narrow_contracts(scope_contracts(user), text)
    today = timezone.localdate()

    if intent in ('apartments', 'amenities'):
        qs = apartments_with_occupancy().filter(building__is_active=True)
        if not allowed(user, OPERATIONS):
            # Users without catalogue management rights see public listings;
            # residents may additionally view their own current unit.
            from django.db.models import Q
            catalogue_scope = Q(is_listed=True, status='available', occupied_now=False)
            if tenant:
                catalogue_scope |= Q(pk__in=scope_contracts(user).filter(status='active', start_date__lte=today, end_date__gte=today).values('apartment_id'))
            qs = qs.filter(catalogue_scope)
        building = re.search(r'\bs\d+\.\d+\b', text)
        if building:
            qs = qs.filter(building__name__icontains=building.group())
        unit = re.search(r'\b(?:can(?: ho)?|phong)\s+([a-z]?\d{3,6})\b', text)
        if unit:
            qs = qs.filter(code__iexact=unit.group(1))
        if intent == 'apartments':
            qs = qs.filter(status='available', occupied_now=False)
            for match in re.finditer(r'(duoi|toi da|khong qua|tren|tu)\s+(\d+(?:[.,]\d+)?)\s*(trieu|tr|dong|vnd)\b', text):
                operator, number, scale = match.groups()
                amount = Decimal(number.replace(',', '.')) * (1000000 if scale in ('trieu', 'tr') else 1)
                if amount > 99999999999999:
                    return {'answer': 'Mức giá vượt phạm vi dữ liệu. Hãy nhập số tiền nhỏ hơn 100 nghìn tỷ đồng.', 'sources': []}
                lookup = {'duoi': 'rent__lt', 'toi da': 'rent__lte', 'khong qua': 'rent__lte', 'tren': 'rent__gt', 'tu': 'rent__gte'}[operator]
                qs = qs.filter(**{lookup: amount})
            total = qs.count()
            lines = [f'Tìm thấy {total} căn hộ còn trống hiện tại trong phạm vi bạn được xem (hiển thị tối đa {LIMIT}):']
            lines.extend(f'- {a.code} · {a.building.name}: {a.area:g} m², tầng {a.floor}, {money(a.rent)}/tháng.' for a in qs.order_by('rent', 'pk')[:LIMIT])
            lines.append('Tình trạng tính tại hôm nay; lịch thuê tương lai và điều khoản cần được quản lý xác nhận trước khi ký.')
            return response('Căn hộ còn trống', lines)
        units = list(qs.order_by('building__name', 'code')[:LIMIT])
        links = ApartmentAmenity.objects.filter(apartment_id__in=[a.pk for a in units]).select_related('amenity').order_by('pk')[:200]
        by_unit = {}
        for link in links:
            by_unit.setdefault(link.apartment_id, []).append(f'{link.amenity.name} × {link.quantity}')
        lines = ['Danh mục tiện ích TRONG CĂN HỘ (hệ thống chưa có danh mục tiện ích chung riêng cho từng tòa):']
        lines.extend(f'- {a.code} · {a.building.name}: ' + (', '.join(by_unit.get(a.pk, [])) or 'Chưa cập nhật tiện ích.') for a in units)
        if not units:
            lines.append('Không tìm thấy căn hộ phù hợp trong phạm vi bạn được xem.')
        if qs.count() > LIMIT:
            lines.append(f'Chỉ hiển thị {LIMIT} căn đầu; hãy nêu tòa và mã căn để thu hẹp kết quả.')
        return response('Tiện ích căn hộ', lines)

    if intent == 'contracts':
        qs = contracts.select_related('apartment__building')
        if 'sap het han' in text:
            from datetime import timedelta
            qs = qs.filter(status='active', end_date__gte=today, end_date__lte=today + timedelta(days=30))
        total = qs.count()
        lines = [f'Tìm thấy {total} hợp đồng trong phạm vi bạn được xem (hiển thị tối đa {LIMIT}):']
        for c in qs.order_by('end_date', 'pk')[:LIMIT]:
            lines.append(f'- {c.code} · {c.apartment.code} · {c.apartment.building.name}: {c.get_status_display()}, '
                         f'{c.start_date:%d/%m/%Y}–{c.end_date:%d/%m/%Y}; cọc {money(c.deposit_amount)} ({c.get_deposit_status_display()}).')
        lines.append('Tiền thuê đã thỏa thuận cần đối chiếu nội dung hợp đồng; giá danh mục hiện tại không thay thế giá hợp đồng.')
        return response('Hợp đồng', lines)

    if intent == 'payments':
        if not tenant and not allowed(user, FINANCE):
            return {'answer': 'Bạn không có quyền tra cứu thanh toán và công nợ. Vui lòng liên hệ quản lý/kế toán.', 'sources': []}
        qs = Payment.objects.filter(contract__in=contracts).select_related('contract')
        paid = 'da thanh toan' in text and 'chua thanh toan' not in text
        qs = qs.filter(status='paid' if paid else 'pending')
        if 'qua han' in text:
            qs = qs.filter(due_date__lt=today)
        month = re.search(r'thang\s+(\d{1,2})(?:[/-](\d{4}))?\b', text)
        period = 'Tất cả kỳ thanh toán.'
        if month or 'thang nay' in text:
            m, y = (int(month[1]), int(month[2]) if month[2] else today.year) if month else (today.month, today.year)
            if not 1 <= m <= 12 or not 1900 <= y <= 9999:
                return {'answer': 'Tháng không hợp lệ. Hãy nhập tháng/năm, ví dụ tháng 10/2026.', 'sources': []}
            qs = qs.filter(due_date__month=m, due_date__year=y)
            period = f'Kỳ {m:02d}/{y} theo hạn thanh toán.'
        if 'tien thue' in text:
            qs = qs.filter(kind='rent')
        elif 'phi dich vu' in text or 'phi quan ly' in text:
            qs = qs.filter(kind='service')
        total = qs.aggregate(amount=Sum('amount'))['amount'] or 0
        lines = [period, f'Tổng {"đã thanh toán" if paid else "còn phải thanh toán"}: {money(total)}; {qs.count()} khoản phù hợp.']
        if not qs.exists():
            lines.append('Không có khoản thu phù hợp trong phạm vi được xem; kết quả không xác nhận nghĩa vụ của hợp đồng ngoài quyền truy cập.')
        for p in qs.order_by('due_date', 'pk')[:LIMIT]:
            lines.append(f'- {p.contract.code} · {p.get_kind_display()}: {money(p.amount)}, hạn {p.due_date:%d/%m/%Y}, {p.get_status_display()}.' +
                         (f' Ngày thu {p.paid_date:%d/%m/%Y}.' if p.paid_date else ''))
        if qs.count() > LIMIT:
            lines.append(f'Hiển thị {LIMIT} khoản đầu; tổng tiền đã tính toàn bộ khoản phù hợp.')
        return response('Thanh toán và công nợ', lines)

    if not tenant and not allowed(user, OPERATIONS):
        return {'answer': 'Bạn không có quyền tra cứu yêu cầu bảo trì.', 'sources': []}
    qs = MaintenanceRequest.objects.select_related('apartment__building')
    if tenant:
        qs = qs.filter(submitted_by=user)
    if code:
        qs = qs.filter(apartment_id__in=contracts.values('apartment_id'))
    lines = [f'Tìm thấy {qs.count()} yêu cầu bảo trì trong phạm vi bạn được xem (hiển thị tối đa {LIMIT}):']
    for ticket in qs.order_by('-created_at', '-pk')[:LIMIT]:
        lines.append(f'- #{ticket.pk} · {ticket.apartment.code} · {ticket.apartment.building.name}: '
                     f'{ticket.get_status_display()} ({ticket.get_priority_display()}); {ticket.content[:250]}. '
                     f'Phản hồi: {ticket.notes[:250] or "Chưa có ghi chú xử lý"}.')
    return response('Yêu cầu bảo trì', lines)
