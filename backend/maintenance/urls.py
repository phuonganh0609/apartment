from config.crud import resource_urls
from .views import maintenance

app_name = "maintenance"
urlpatterns = resource_urls(maintenance)
