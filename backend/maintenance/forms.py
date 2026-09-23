from config.forms import StyledModelForm
from .models import MaintenanceRequest


class MaintenanceForm(StyledModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ["apartment", "content", "priority", "status", "notes"]
