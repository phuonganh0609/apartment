from accounts.permissions import OPERATIONS
from config.crud import Resource
from .forms import MaintenanceForm
from .models import MaintenanceRequest

maintenance = Resource(
    MaintenanceRequest,
    MaintenanceForm,
    "Bảo trì",
    "maintenance",
    "maintenance",
    (
        ("apartment", "Căn hộ"),
        ("content", "Yêu cầu"),
        ("priority", "Ưu tiên"),
        ("status", "Trạng thái"),
        ("created_at", "Ngày tạo"),
    ),
    search=("content", "apartment__code"),
    filters=(
        ("status", "Trạng thái", MaintenanceRequest.Status.choices),
        ("priority", "Ưu tiên", MaintenanceRequest.Priority.choices),
    ),
    read_roles=OPERATIONS,
    related=("apartment__building",),
    order_fields=("pk", "created_at"),
)
