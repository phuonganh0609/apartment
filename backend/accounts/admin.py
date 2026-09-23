from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class AccountAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Nghiep vu", {"fields": ("full_name", "role", "can_edit_deposit")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Nghiep vu", {"fields": ("full_name", "role", "can_edit_deposit")}),
    )
    list_display = ("username", "full_name", "role", "is_active")
