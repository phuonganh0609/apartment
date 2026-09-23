from django.contrib import admin
from .models import Building, Apartment, Amenity, ApartmentAmenity

admin.site.register(Building)
admin.site.register(Apartment)
admin.site.register(Amenity)
admin.site.register(ApartmentAmenity)
