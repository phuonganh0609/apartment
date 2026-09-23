from django.urls import path
from . import views

app_name = "ai_assistant"
urlpatterns = [
    path(
        "contracts/<int:pk>/summary/", views.summary, name="contract_summary"
    ),
    path(
        "contracts/<int:pk>/notification/",
        views.notification,
        name="notification",
    ),
    path("chatbot/", views.chatbot, name="chatbot"),
]
