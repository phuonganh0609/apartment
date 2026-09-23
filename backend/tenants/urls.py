from config.crud import resource_urls
from .views import contacts, tenants

app_name = "tenants"
urlpatterns = resource_urls(contacts, "contacts/") + resource_urls(tenants)
