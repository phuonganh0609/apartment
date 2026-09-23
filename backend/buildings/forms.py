from config.forms import StyledModelForm
from .models import Amenity, Apartment, ApartmentAmenity, Building


class BuildingForm(StyledModelForm):
    class Meta:
        model = Building
        fields = ["name", "address", "description", "is_active"]


class ApartmentForm(StyledModelForm):
    class Meta:
        model = Apartment
        fields = ["building", "code", "floor", "area", "rent", "status"]


class AmenityForm(StyledModelForm):
    class Meta:
        model = Amenity
        fields = ["name", "description", "is_active"]


class ApartmentAmenityForm(StyledModelForm):
    class Meta:
        model = ApartmentAmenity
        fields = ["apartment", "amenity", "quantity", "notes"]
