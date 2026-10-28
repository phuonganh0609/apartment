from django import forms
from config.forms import StyledModelForm
from .models import Amenity, Apartment, ApartmentAmenity, Building


class BuildingForm(StyledModelForm):
    class Meta:
        model = Building
        fields = ["name", "address", "description", "is_active"]


class ApartmentForm(StyledModelForm):
    def clean_photo_url(self):
        value = self.cleaned_data.get("photo_url", "")
        if value and not value.startswith("https://"):
            raise forms.ValidationError("Ảnh công khai phải dùng đường dẫn HTTPS.")
        return value

    class Meta:
        model = Apartment
        fields = ["building", "code", "floor", "area", "rent", "status", "is_listed", "public_description", "photo_url"]


class AmenityForm(StyledModelForm):
    class Meta:
        model = Amenity
        fields = ["name", "description", "is_active"]


class ApartmentAmenityForm(StyledModelForm):
    class Meta:
        model = ApartmentAmenity
        fields = ["apartment", "amenity", "quantity", "notes"]
