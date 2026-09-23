from config.crud import Resource
from .forms import (
    AmenityForm,
    ApartmentAmenityForm,
    ApartmentForm,
    BuildingForm,
)
from .models import Amenity, Apartment, ApartmentAmenity, Building
from .services import apartments_with_occupancy

buildings = Resource(
    Building,
    BuildingForm,
    "Tòa nhà",
    "buildings",
    "building",
    (("name", "Tòa nhà"), ("address", "Địa chỉ"), ("is_active", "Hoạt động")),
    search=("name", "address"),
    order_fields=("pk", "name"),
)
apartments = Resource(
    Apartment,
    ApartmentForm,
    "Căn hộ",
    "buildings",
    "apartment",
    (
        ("code", "Căn hộ"),
        ("building", "Tòa nhà"),
        ("area", "Diện tích m²"),
        ("rent", "Giá thuê / tháng"),
        ("occupancy_label", "Tình trạng"),
    ),
    search=("code", "building__name"),
    queryset=apartments_with_occupancy,
    filters=(
        (
            "building_id",
            "Tòa nhà",
            lambda: Building.objects.values_list("pk", "name"),
        ),
        ("status", "Vận hành", Apartment.Status.choices),
        (
            "occupied_now",
            "Tình trạng thuê",
            ((1, "Đang cho thuê"), (0, "Chưa có khách")),
        ),
    ),
    order_fields=("pk", "code", "rent", "area"),
    extra_context=lambda request, obj: {
        "amenity_links": (
            obj.amenity_links.select_related("amenity") if obj else []
        )
    },
)
amenities = Resource(
    Amenity,
    AmenityForm,
    "Tiện ích",
    "buildings",
    "amenity",
    (
        ("name", "Tiện ích"),
        ("description", "Mô tả"),
        ("is_active", "Đang dùng"),
    ),
    search=("name",),
)
links = Resource(
    ApartmentAmenity,
    ApartmentAmenityForm,
    "Tiện ích căn hộ",
    "buildings",
    "apartment_amenity",
    (
        ("apartment", "Căn hộ"),
        ("amenity", "Tiện ích"),
        ("quantity", "Số lượng"),
        ("notes", "Ghi chú"),
    ),
    search=("apartment__code", "amenity__name"),
    related=("apartment__building", "amenity"),
)
