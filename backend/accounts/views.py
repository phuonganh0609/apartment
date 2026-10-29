import hashlib

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetView
from django.conf import settings
from smtplib import SMTPException
import logging
from django.core.cache import cache

from config.crud import Resource
from .forms import UserForm, TenantRegistrationForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django import forms
from config.forms import StyledModelForm
from tenants.models import Tenant


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("reports:dashboard")
    form = TenantRegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        address = request.META.get("REMOTE_ADDR", "")
        key = "tenant-register:" + hashlib.sha256(address.encode()).hexdigest()
        if not cache.add(key, 1, 60):
            form.add_error(None, "Vui lòng chờ một phút trước khi tạo thêm tài khoản.")
        else:
            form.save()
            messages.success(request, "Đăng ký thành công. Hãy đăng nhập; quản lý sẽ liên kết hồ sơ thuê của bạn sau khi xác minh.")
            return redirect("accounts:login")
    return render(request, "accounts/register.html", {"form": form})


class ResetPasswordView(PasswordResetView):
    def form_valid(self, form):
        address = self.request.META.get("REMOTE_ADDR", "")
        key = "reset-request:" + hashlib.sha256(address.encode()).hexdigest()
        if not cache.add(key, 1, 60):
            try:
                count = cache.incr(key)
            except ValueError:
                cache.set(key, 1, 60)
                count = 1
            if count > 5:
                form.add_error(None, "Bạn đã yêu cầu nhiều lần. Vui lòng thử lại sau một phút.")
                return self.form_invalid(form)
        if settings.EMAIL_BACKEND.endswith("smtp.EmailBackend") and not settings.EMAIL_HOST:
            form.add_error(None, "Chức năng gửi email chưa được cấu hình. Vui lòng liên hệ quản lý.")
            return self.form_invalid(form)
        try:
            return super().form_valid(form)
        except (SMTPException, OSError):
            logging.getLogger(__name__).warning("Password reset email delivery failed")
            form.add_error(None, "Dịch vụ email tạm thời không khả dụng. Vui lòng thử lại sau.")
            return self.form_invalid(form)


class TenantProfileForm(StyledModelForm):
    class Meta:
        model = Tenant
        fields = ("full_name", "phone", "email", "address")


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    form = None
    if request.user.role == "tenant" and request.user.tenant_id:
        form = TenantProfileForm(
            request.POST if request.method == "POST" else None,
            instance=request.user.tenant,
        )
        if request.method == "POST" and form.is_valid():
            tenant = form.save()
            User.objects.filter(pk=request.user.pk).update(
                full_name=tenant.full_name, email=tenant.email
            )
            messages.success(request, "Đã cập nhật hồ sơ cá nhân.")
            return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {
        "title": "Tài khoản cá nhân", "profile_form": form,
    })


class ThrottledLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_superuser and not self.get_redirect_url():
            from django.urls import reverse
            return reverse("admin_dashboard")
        return super().get_success_url()

    def form_valid(self, form):
        if cache.get(self.attempt_key(), 0) >= 10:
            form.add_error(
                None,
                (
                    "Quá nhiều lần thử. Vui lòng chờ 5 ph"
                    "út rồi đăng nhập lại."
                ),
            )
            return self.form_invalid(form)
        cache.delete(self.attempt_key())
        return super().form_valid(form)

    def attempt_key(self):
        value = (
            self.request.META.get("REMOTE_ADDR", "")
            + "|"
            + self.request.POST.get("username", "").lower()
        )
        return "login:" + hashlib.sha256(value.encode()).hexdigest()

    def form_invalid(self, form):
        key = self.attempt_key()
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, 300)
        if attempts >= 10:
            form.add_error(
                None, "Tạm khóa đăng nhập 5 phút do nhiều lần thử thất bại."
            )
        return super().form_invalid(form)


def account_delete_context(request, obj):
    from django.urls import reverse
    return {'delete_url': reverse('accounts:user_delete', args=[obj.pk])
            if obj and request.user.is_superuser and obj.pk != request.user.pk else None}


@login_required
@require_http_methods(['GET', 'POST'])
def delete_account(request, pk):
    from django.core.exceptions import PermissionDenied
    from django.shortcuts import get_object_or_404
    from django.db import transaction
    from .models import User, AuditEvent

    if not request.user.is_active or not request.user.is_superuser:
        raise PermissionDenied
    if pk == request.user.pk:
        raise PermissionDenied('Không thể tự xóa tài khoản đang đăng nhập.')
    account = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            account = get_object_or_404(User.objects.select_for_update(), pk=pk)
            username = account.username
            account.delete()
            AuditEvent.objects.create(actor=request.user.username,
                action='account_deleted', detail=f'Đã xóa tài khoản {username} (ID {pk}).')
        messages.success(request, 'Đã xóa tài khoản. Hồ sơ khách thuê và dữ liệu nghiệp vụ vẫn được giữ lại.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_delete.html', {
        'title': 'Xóa tài khoản', 'object': account,
    })


users = Resource(
    User,
    UserForm,
    "Tài khoản",
    "accounts",
    "user",
    (
        ("username", "Tên đăng nhập"),
        ("full_name", "Họ tên"),
        ("role", "Vai trò"),
        ("is_active", "Hoạt động"),
    ),
    search=("username", "full_name"),
    read_roles=("manager",),
    write_roles=("manager",),
    deletable=False,
    extra_context=account_delete_context,
    filters=(("role", "Vai trò", User.Role.choices),),
    form_options=lambda request, obj: {"actor": request.user},
    order_fields=("pk", "username", "full_name"),
)
