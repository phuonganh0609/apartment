from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render
from .models import User, SystemSettings, AuditEvent
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.management import call_command, CommandError
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from pathlib import Path
from io import StringIO


class SettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ("contact_phone", "contact_email", "expiry_warning_days")

    def clean_expiry_warning_days(self):
        value = self.cleaned_data["expiry_warning_days"]
        if not 1 <= value <= 365:
            raise forms.ValidationError("Chọn từ 1 đến 365 ngày.")
        return value


@login_required
@require_http_methods(["GET", "POST"])
def admin_section(request, section):
    if not request.user.is_active or not request.user.is_superuser:
        raise PermissionDenied
    titles = {"roles": "Vai trò & Phân quyền", "data": "Dữ liệu hệ thống", "settings": "Cấu hình hệ thống", "logs": "Nhật ký hoạt động", "backups": "Sao lưu & Khôi phục"}
    context = {"title": titles[section], "admin_section": section}
    if section == "settings":
        config, _ = SystemSettings.objects.get_or_create(pk=1)
        form = SettingsForm(request.POST if request.method == "POST" else None, instance=config)
        if request.method == "POST" and form.is_valid():
            form.save()
            AuditEvent.objects.create(actor=request.user.username, action="Lưu cấu hình hệ thống")
            messages.success(request, "Đã lưu cấu hình.")
            return redirect("admin_settings")
        context["form"] = form
    elif section == "logs":
        query = request.GET.get("q", "").strip()[:100]
        events = AuditEvent.objects.all()
        if query:
            from django.db.models import Q
            events = events.filter(Q(actor__icontains=query) | Q(action__icontains=query) | Q(detail__icontains=query))
        context.update(events=Paginator(events, 25).get_page(request.GET.get("page")), query=query)
    elif section == "data":
        from buildings.models import Building, Apartment
        from contracts.models import Contract
        from payments.models import Payment
        context["data_counts"] = [("Tòa nhà", Building.objects.count(), "/buildings/"), ("Căn hộ", Apartment.objects.count(), "/buildings/apartments/"), ("Hợp đồng", Contract.objects.count(), "/contracts/"), ("Thanh toán", Payment.objects.count(), "/payments/")]
    elif section == "backups":
        if request.method == "POST":
            try:
                call_command("backup_database", stdout=StringIO())
                AuditEvent.objects.create(actor=request.user.username, action="Tạo sao lưu SQLite")
                messages.success(request, "Đã tạo bản sao lưu CSDL.")
            except (CommandError, OSError) as exc:
                messages.error(request, "Không thể sao lưu. Kiểm tra CSDL và quyền lưu trữ.")
            return redirect("admin_backups")
        folder = Path(settings.DATA_DIR) / "backups"
        context["backups"] = [{"name": p.name, "size": p.stat().st_size} for p in sorted(folder.glob("*.sqlite3"), reverse=True) if p.is_file()]
    return render(request, "accounts/admin_section.html", context)


@login_required
def admin_dashboard(request):
    if not request.user.is_active or not request.user.is_superuser:
        raise PermissionDenied
    users = User.objects.all()
    from buildings.models import Building
    return render(request, "accounts/admin_dashboard.html", {
        "title": "Quản trị hệ thống",
        "total_users": users.count(),
        "building_count": Building.objects.count(),
        "active_users": users.filter(is_active=True).count(),
        "locked_users": users.filter(is_active=False).count(),
        "unlinked_tenants": users.filter(role="tenant", tenant__isnull=True).count(),
        "role_counts": users.values("role").annotate(total=Count("pk")).order_by("role"),
        "recent_users": users.order_by("-date_joined")[:10],
    })
