from django.urls import path
from config.crud import resource_urls
from . import views

app_name = "regulations"
urlpatterns = [
    path("documents/new/", views.upload, name="document_upload"),
    path(
        "documents/<int:pk>/download/",
        views.download,
        name="document_download",
    ),
    path(
        "documents/<int:pk>/delete/",
        views.delete_document,
        name="document_delete",
    ),
] + resource_urls(views.regulations)
