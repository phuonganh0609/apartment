from config.forms import StyledModelForm
from .models import Payment


class PaymentForm(StyledModelForm):
    class Meta:
        model = Payment
        fields = [
            "contract",
            "kind",
            "amount",
            "due_date",
            "status",
            "paid_date",
        ]
