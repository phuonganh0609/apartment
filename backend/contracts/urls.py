from django.urls import path
from config.crud import resource_urls
from . import views

app_name = "contracts"
urlpatterns = [
    path("deposits/", views.deposits, name="deposit_list"),
    path("<int:pk>/deposit/", views.deposit_edit, name="deposit_edit"),
    path("<int:pk>/extend/", views.extend, name="contract_extend"),
    path("<int:pk>/terminate/", views.terminate, name="contract_terminate"),
] + resource_urls(views.contracts)
