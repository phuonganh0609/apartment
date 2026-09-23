from django.urls import path
from .views import alerts

app_name = "alerts"
urlpatterns = [path("", alerts, name="alert_list")]
