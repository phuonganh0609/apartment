from config.crud import resource_urls
from .views import amenities, apartments, buildings, links

app_name = "buildings"
urlpatterns = (
    resource_urls(apartments, "apartments/")
    + resource_urls(buildings)
    + resource_urls(amenities, "amenities/")
    + resource_urls(links, "apartment-amenities/")
)
