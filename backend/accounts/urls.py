from django.contrib.auth.views import LogoutView
from django.urls import path
from config.crud import resource_urls
from .views import ThrottledLoginView, users

app_name = "accounts"
urlpatterns = [
    path("login/", ThrottledLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
] + resource_urls(users, "users/")
