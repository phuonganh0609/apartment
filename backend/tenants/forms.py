from config.forms import StyledModelForm
from .models import Contact, Tenant


class TenantForm(StyledModelForm):
    class Meta:
        model = Tenant
        fields = ["full_name", "phone", "email", "identity_number", "address"]


class ContactForm(StyledModelForm):
    class Meta:
        model = Contact
        fields = ["tenant", "full_name", "relationship", "phone", "email"]
