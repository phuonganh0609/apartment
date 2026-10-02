from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("buildings/", include("buildings.urls")),
    path("tenants/", include("tenants.urls")),
    path("contracts/", include("contracts.urls")),
    path("payments/", include("payments.urls")),
    path("maintenance/", include("maintenance.urls")),
    path("alerts/", include("alerts.urls")),
    path("regulations/", include("regulations.urls")),
    path("ai/", include("ai_assistant.urls")),
    path("", include("reports.urls")),
]
admin.site.site_header = "Quản trị An Cư"
admin.site.site_title = "An Cư"
