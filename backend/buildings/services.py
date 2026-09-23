from django.db.models import Exists, OuterRef
from django.utils import timezone
from contracts.models import Contract
from .models import Apartment


def apartments_with_occupancy():
    today = timezone.localdate()
    active = Contract.objects.filter(
        apartment_id=OuterRef("pk"),
        status="active",
        start_date__lte=today,
        end_date__gte=today,
    )
    return Apartment.objects.select_related("building").annotate(
        occupied_now=Exists(active)
    )
