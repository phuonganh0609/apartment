from django.urls import include, path
from accounts.portal import tenant_portal
from accounts.admin_portal import admin_dashboard, admin_section
from accounts.views import ThrottledLoginView

urlpatterns = [
    path("admin/", admin_dashboard, name="admin_dashboard"),
    path("admin/roles/", admin_section, {"section": "roles"}, name="admin_roles"),
    path("admin/data/", admin_section, {"section": "data"}, name="admin_data"),
    path("admin/settings/", admin_section, {"section": "settings"}, name="admin_settings"),
    path("admin/logs/", admin_section, {"section": "logs"}, name="admin_logs"),
    path("admin/backups/", admin_section, {"section": "backups"}, name="admin_backups"),

    path("admin/login/", ThrottledLoginView.as_view(), name="admin_login"),
    path("my-home/", tenant_portal, name="tenant_portal"),
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
