from django.urls import path
from . import views

app_name = "reports"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("reports/occupancy/", views.occupancy, name="occupancy_report"),
    path("reports/revenue/", views.revenue, name="revenue_report"),
    path("reports/debts/", views.debts, name="debt_report"),
]
