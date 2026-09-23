from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from buildings.models import Apartment
from .models import Contract


@transaction.atomic
def save_contract(contract):
    # Serialize overlapping reservations on PostgreSQL; SQLite serializes
    # writes.
    Apartment.objects.select_for_update().get(pk=contract.apartment_id)
    if contract.pk:
        previous = Contract.objects.select_for_update().get(pk=contract.pk)
        # Do not overwrite a deposit changed concurrently from its dedicated
        # screen.
        contract.deposit_amount = previous.deposit_amount
        if previous.status == Contract.Status.TERMINATED:
            raise ValidationError("Hợp đồng đã thanh lý không được thay đổi.")
        if (
            previous.status == Contract.Status.ACTIVE
            and contract.status == Contract.Status.DRAFT
        ):
            raise ValidationError(
                "Hợp đồng đã ký không được chuyển về bản nháp."
            )
    contract.full_clean()
    contract.save()
    return contract


@transaction.atomic
def extend_contract(pk, new_end_date):
    apartment_id = (
        Contract.objects.only("apartment_id").get(pk=pk).apartment_id
    )
    Apartment.objects.select_for_update().get(pk=apartment_id)
    contract = Contract.objects.select_for_update().get(pk=pk)
    if contract.status != Contract.Status.ACTIVE:
        raise ValidationError("Chỉ gia hạn hợp đồng đã ký, chưa thanh lý.")
    if (
        new_end_date <= contract.end_date
        or new_end_date <= timezone.localdate()
    ):
        raise ValidationError(
            "Ngày gia hạn phải sau ngày kết thúc hiện tại và sau hôm nay."
        )
    contract.end_date = new_end_date
    return save_contract(contract)


@transaction.atomic
def terminate_contract(pk):
    contract = Contract.objects.select_for_update().get(pk=pk)
    if contract.status != Contract.Status.ACTIVE:
        raise ValidationError("Chỉ thanh lý hợp đồng đã ký.")
    contract.status = Contract.Status.TERMINATED
    contract.save(update_fields=["status"])
    return contract
