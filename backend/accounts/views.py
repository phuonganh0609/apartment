import hashlib

from django.contrib.auth.views import LoginView
from django.core.cache import cache

from config.crud import Resource
from .forms import UserForm
from .models import User


class ThrottledLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

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
    filters=(("role", "Vai trò", User.Role.choices),),
    form_options=lambda request, obj: {"actor": request.user},
    order_fields=("pk", "username", "full_name"),
)
