from config.crud import Resource
from .forms import ContactForm, TenantForm
from .models import Contact, Tenant

tenants = Resource(
    Tenant,
    TenantForm,
    "Khách thuê",
    "tenants",
    "tenant",
    (
        ("full_name", "Họ tên"),
        ("phone", "Điện thoại"),
        ("email", "Email"),
        ("address", "Địa chỉ"),
    ),
    search=("full_name", "phone", "email"),
    order_fields=("pk", "full_name"),
    extra_context=lambda request, obj: {
        "contacts": obj.contacts.all() if obj else []
    },
)
contacts = Resource(
    Contact,
    ContactForm,
    "Người liên hệ",
    "tenants",
    "contact",
    (
        ("full_name", "Họ tên"),
        ("tenant", "Khách thuê"),
        ("relationship", "Quan hệ"),
        ("phone", "Điện thoại"),
    ),
    search=("full_name", "tenant__full_name"),
    related=("tenant",),
)
