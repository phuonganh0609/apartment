from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.urls import path
from config.crud import resource_urls
from .views import ThrottledLoginView, users, profile, ResetPasswordView

app_name = "accounts"
urlpatterns = [
    path("password-reset/", ResetPasswordView.as_view(
        template_name="accounts/reset_request.html",
        email_template_name="accounts/reset_email.txt",
        subject_template_name="accounts/reset_subject.txt",
        success_url=reverse_lazy("accounts:password_reset_done"),
    ), name="password_reset"),
    path("password-reset/sent/", PasswordResetDoneView.as_view(
        template_name="accounts/reset_done.html",
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
        template_name="accounts/reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete"),
    ), name="password_reset_confirm"),
    path("reset/complete/", PasswordResetCompleteView.as_view(
        template_name="accounts/reset_complete.html",
    ), name="password_reset_complete"),
    path("profile/", profile, name="profile"),
    path("password/", PasswordChangeView.as_view(
        template_name="accounts/password_change.html",
        success_url=reverse_lazy("accounts:profile"),
        extra_context={"title": "Đổi mật khẩu"},
    ), name="password_change"),
    path("login/", ThrottledLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
] + resource_urls(users, "users/")
