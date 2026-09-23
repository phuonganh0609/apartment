from django import forms
from config.forms import StyledModelForm
from .models import Contract


class ContractForm(StyledModelForm):
    class Meta:
        model = Contract
        fields = [
            "code",
            "apartment",
            "tenant",
            "start_date",
            "end_date",
            "status",
            "contract_content",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Terminal state is only available through a separate, confirmed
        # action.
        self.fields["status"].choices = Contract.Status.choices[:2]
        if (
            self.instance.pk
            and self.instance.status == Contract.Status.TERMINATED
        ):
            for field in self.fields.values():
                field.disabled = True
            self.fields["status"].choices = Contract.Status.choices

    def clean(self):
        data = super().clean()
        if self.instance.pk:
            original = Contract.objects.get(pk=self.instance.pk)
            if original.status == Contract.Status.TERMINATED:
                raise forms.ValidationError(
                    "Hợp đồng đã thanh lý được giữ nguyên để tra cứu lịch sử."
                )
            if (
                original.status == Contract.Status.ACTIVE
                and data.get("status") == Contract.Status.DRAFT
            ):
                raise forms.ValidationError(
                    (
                        "Không chuyển hợp đồng đã ký về bản n"
                        "háp. Dùng chức năng thanh lý."
                    )
                )
            if original.payments.exists() and any(
                data.get(key) != getattr(original, key)
                for key in ("apartment", "tenant")
            ):
                raise forms.ValidationError(
                    (
                        "Hợp đồng có thanh toán không được đổ"
                        "i căn hộ hoặc khách thuê."
                    )
                )
        return data


class DepositForm(StyledModelForm):
    class Meta:
        model = Contract
        fields = ["deposit_amount"]


class ExtendForm(forms.Form):
    end_date = forms.DateField(
        label="Ngày kết thúc mới",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
    )
