from django import forms
from django.contrib.auth.password_validation import validate_password

from config.forms import StyledModelForm
from .models import User
from django.contrib.auth.forms import UserCreationForm


class TenantRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng. Hãy đăng nhập hoặc khôi phục mật khẩu.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TENANT
        user.tenant = None
        user.is_staff = False
        user.is_superuser = False
        user.can_edit_deposit = False
        if commit:
            user.save()
        return user


class UserForm(StyledModelForm):
    new_password = forms.CharField(
        label="Mật khẩu mới",
        required=False,
        widget=forms.PasswordInput,
        help_text=(
            "Bắt buộc khi tạo tài khoản. Để trống"
            " khi giữ mật khẩu hiện tại."
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "full_name",
            "email",
            "role",
            "tenant",
            "can_edit_deposit",
            "can_ai_payment_notice",
            "can_ai_renewal_notice",
            "is_active",
        ]

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        password = data.get("new_password")
        if data.get("role") == "tenant" and not data.get("tenant"):
            self.add_error("tenant", "Chọn hồ sơ khách thuê cho tài khoản này.")
        if data.get("role") != "tenant":
            data["tenant"] = None
        if data.get("role") in ("staff", "tenant"):
            data["can_edit_deposit"] = False
        if data.get("role") == "tenant":
            data["can_ai_payment_notice"] = False
            data["can_ai_renewal_notice"] = False
        if not self.instance.pk and not password:
            self.add_error("new_password", "Nhập mật khẩu cho tài khoản mới.")
        if password:
            validate_password(
                password,
                User(
                    username=data.get("username", ""),
                    full_name=data.get("full_name", ""),
                ),
            )
        if self.actor and self.instance.pk == self.actor.pk:
            if (
                not data.get("is_active")
                or data.get("role") != self.actor.role
            ):
                raise forms.ValidationError(
                    (
                        "Không thể tự khóa hoặc đổi vai trò t"
                        "ài khoản đang sử dụng."
                    )
                )
        if (
            self.instance.is_superuser
            and self.actor
            and not self.actor.is_superuser
        ):
            raise forms.ValidationError(
                "Chỉ quản trị viên hệ thống được sửa tài khoản superuser."
            )
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user
