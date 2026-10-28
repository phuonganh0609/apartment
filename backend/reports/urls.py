from django.urls import path
from django.views.generic import RedirectView
from . import views
from .public import public_page
from accounts.views import register

app_name = "reports"
urlpatterns = [
    path("apartments/", public_page, name="public_apartments"),
    path("apartments/<int:pk>/", public_page, name="public_apartment"),
    path("about/", public_page, {"page": "about"}, name="about"),
    path("contact/", public_page, {"page": "contact"}, name="contact"),
    path("faq/", public_page, {"page": "faq"}, name="faq"),
    path("register/", register, name="register"),
    path("forgot-password/", RedirectView.as_view(pattern_name="accounts:password_reset"), name="forgot"),
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reports/", views.report_center, name="center"),
    path("reports/occupancy/", views.occupancy, name="occupancy_report"),
    path("reports/revenue/", views.revenue, name="revenue_report"),
    path("reports/debts/", views.debts, name="debt_report"),
]
