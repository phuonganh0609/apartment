from django import forms
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from buildings.models import Apartment
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
            "ai_authorized_users",
        ]

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide occupied units from new contracts; also check the requested
        # period on a submitted form. Keep the current unit when editing.
        today = timezone.localdate()
        conflicts = Contract.objects.filter(
            apartment_id=OuterRef('pk'), status=Contract.Status.ACTIVE,
            start_date__lte=today, end_date__gte=today,
        )
        if self.is_bound:
            try:
                start = self.fields['start_date'].clean(self.data.get(self.add_prefix('start_date')))
                end = self.fields['end_date'].clean(self.data.get(self.add_prefix('end_date')))
            except forms.ValidationError:
                pass
            else:
                if start and end and end > start:
                    conflicts = Contract.objects.filter(
                        apartment_id=OuterRef('pk'), status=Contract.Status.ACTIVE,
                    ).filter(Q(start_date__lte=today, end_date__gte=today) |
                             Q(start_date__lte=end, end_date__gte=start))
        if self.instance.pk:
            conflicts = conflicts.exclude(pk=self.instance.pk)
        available = Apartment.objects.select_related('building').annotate(
            has_conflict=Exists(conflicts),
        )
        condition = Q(status='available', building__is_active=True, has_conflict=False)
        if self.instance.pk:
            condition |= Q(pk=self.instance.apartment_id)
        self.fields['apartment'].queryset = available.filter(condition).order_by('building__name', 'code')
        self.fields['apartment'].help_text = 'Chỉ hiển thị căn hộ chưa có khách thuê, không bảo trì và thuộc tòa nhà đang hoạt động.'
        self.fields['apartment'].error_messages['invalid_choice'] = 'Căn hộ không còn trống hoặc đã có hợp đồng trùng thời gian thuê. Vui lòng chọn căn khác.'
        if actor is None or not (actor.is_superuser or actor.role == "manager"):
            self.fields.pop("ai_authorized_users", None)
        else:
            self.fields["ai_authorized_users"].queryset = self.fields["ai_authorized_users"].queryset.filter(is_active=True).exclude(role="tenant")
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
    deposit_status = forms.ChoiceField(
        label="Tình trạng tiền cọc", choices=Contract.DepositStatus.choices,
        required=False,
    )

    def clean_deposit_status(self):
        return self.cleaned_data.get("deposit_status") or self.instance.deposit_status

    class Meta:
        model = Contract
        fields = ["deposit_amount", "deposit_status"]


class ExtendForm(forms.Form):
    end_date = forms.DateField(
        label="Ngày kết thúc mới",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
    )
