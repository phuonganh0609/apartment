"""Project support utility."""

from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parent.parent
apps = {
    "accounts": ["User"],
    "buildings": ["Building", "Apartment", "Amenity", "ApartmentAmenity"],
    "tenants": ["Tenant", "Contact"],
    "contracts": ["Contract"],
    "payments": ["Payment"],
    "maintenance": ["MaintenanceRequest"],
    "alerts": [],
    "reports": [],
    "regulations": ["Regulation", "RegulationDocument"],
    "ai_assistant": [],
}


def create(path, content=""):
    parts = Path(path).parts
    if "templates" in parts and parts[0] in apps:
        path = str(Path("frontend/templates").joinpath(*parts[2:]))
    elif parts[0] in apps:
        path = str(
            Path("chatbot" if parts[0] == "ai_assistant" else "backend") / path
        )
    elif parts[0] == "tests":
        path = str(Path("backend") / path)
    elif parts[0] in {"templates", "static"}:
        path = str(Path("frontend") / path)
    elif parts[0] == "media":
        path = str(Path("data") / path)
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(content, encoding="utf-8")


for name, models in apps.items():
    create(f"{name}/__init__.py")
    config_name = "".join(word.title() for word in name.split("_")) + "Config"
    create(
        f"{name}/apps.py",
        (
            "from django.apps import AppConfig\n\n"
            "\nclass "
            f"{config_name}"
            "(AppConfig):\n    default_auto_field"
            " = 'django.db.models.BigAutoField'\n"
            "    name = '"
            f"{name}"
            "'\n"
        ),
    )
    if models:
        create(f"{name}/migrations/__init__.py")
        if name != "accounts":
            create(
                f"{name}/admin.py",
                "from django.contrib import admin\nfrom .models import "
                + ", ".join(models)
                + "\n\n"
                + "\n".join(
                    f"admin.site.register({model})" for model in models
                )
                + "\n",
            )
create(
    "accounts/admin.py",
    (
        "from django.contrib import admin\nfro"
        "m django.contrib.auth.admin import U"
        "serAdmin\nfrom .models import User\n\n\n"
        "@admin.register(User)\nclass AccountA"
        "dmin(UserAdmin):\n    fieldsets = Use"
        "rAdmin.fieldsets + (('Nghiep vu', {'"
        "fields': ('full_name', 'role', 'can_"
        "edit_deposit')}),)\n    add_fieldsets"
        " = UserAdmin.add_fieldsets + (('Nghi"
        "ep vu', {'fields': ('full_name', 'ro"
        "le', 'can_edit_deposit')}),)\n    lis"
        "t_display = ('username', 'full_name'"
        ", 'role', 'is_active')\n"
    ),
)
resources = {
    "accounts": ["user"],
    "buildings": ["building", "apartment", "amenity", "apartment_amenity"],
    "tenants": ["tenant", "contact"],
    "contracts": ["contract"],
    "payments": ["payment"],
    "maintenance": ["maintenance"],
    "regulations": ["regulation"],
}
for app, names in resources.items():
    for name in names:
        for action in ["list", "form", "detail"]:
            create(
                f"{app}/templates/{app}/{name}_{action}.html",
                "{% extends 'generic/" + action + ".html' %}\n",
            )
for directory in [
    "ai_assistant/services",
    "ai_assistant/prompts",
    "tests",
    "accounts/management",
    "accounts/management/commands",
]:
    create(directory + "/__init__.py")
for directory in [
    "media/contracts",
    "media/regulations",
    "static/images",
    "docs/screenshots",
    "static/vendor",
]:
    create(directory + "/.gitkeep")
for code, title, message in [
    (
        403,
        "Không có quyền truy cập",
        "Vai trò của bạn chưa được cấp quyền sử dụng chức năng này.",
    ),
    (
        404,
        "Không tìm thấy trang",
        "Đường dẫn hoặc dữ liệu bạn cần không còn tồn tại.",
    ),
    (
        500,
        "Không thể xử lý yêu cầu",
        "Vui lòng thử lại hoặc liên hệ người quản lý hệ thống.",
    ),
]:
    create(
        f"templates/{code}.html",
        (
            '<!doctype html><html lang="vi"><meta'
            ' charset="utf-8"><meta name="viewpor'
            't" content="width=device-width, init'
            'ial-scale=1"><title>'
        )
        + title
        + (
            '</title><body style="font-family:Seg'
            "oe UI,Arial;background:#f5f8f6;color"
            ':#254b3b;padding:10vh 10vw"><h1>'
        )
        + str(code)
        + " · "
        + title
        + "</h1><p>"
        + message
        + '</p><a href="/">Về trang tổng quan</a></body></html>',
    )
env = (
    (ROOT / ".env.example")
    .read_text(encoding="utf-8")
    .replace("replace-with-a-long-random-secret", secrets.token_urlsafe(48))
)
create(".env", env)
print("Support packages, template wrappers and local configuration are ready.")
