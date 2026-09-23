from django.urls import path
from config.crud import resource_urls
from .views import debts, payments

app_name = "payments"
urlpatterns = [path("debts/", debts, name="debt_list")] + resource_urls(
    payments
)
