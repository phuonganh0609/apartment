import os
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from buildings.services import apartments_with_occupancy
from regulations.models import Regulation


def listings():
    return apartments_with_occupancy().filter(
        is_listed=True, building__is_active=True,
        status="available", occupied_now=False,
    ).select_related("building")


def public_page(request, page="apartments", pk=None):
    context = {"page": page, "contact_phone": os.getenv("PUBLIC_CONTACT_PHONE", ""),
               "contact_email": os.getenv("PUBLIC_CONTACT_EMAIL", "")}
    from accounts.models import SystemSettings
    config = SystemSettings.objects.filter(pk=1).first()
    if config:
        context.update(contact_phone=config.contact_phone, contact_email=config.contact_email)
    if pk is not None:
        context["apartment"] = get_object_or_404(listings().prefetch_related("amenity_links__amenity"), pk=pk)
        context["page"] = "detail"
    elif page == "apartments":
        qs = listings()
        query = request.GET.get("q", "").strip()[:200]
        if query:
            qs = qs.filter(Q(building__address__icontains=query) | Q(building__name__icontains=query) | Q(code__icontains=query))
        errors = []
        for name, lookup in (("min_price", "rent__gte"), ("max_price", "rent__lte")):
            raw = request.GET.get(name, "").strip()[:30]
            if raw:
                try:
                    number = Decimal(raw)
                    if not number.is_finite() or not 0 <= number <= 99999999999999:
                        raise InvalidOperation
                    qs = qs.filter(**{lookup: number})
                except InvalidOperation:
                    errors.append("Giá thuê phải là số không âm hợp lệ.")
            context[name] = raw
        sort = request.GET.get("sort", "rent")
        if sort not in ("rent", "-rent", "area", "-area"):
            sort = "rent"
        context.update(query=query, sort=sort, errors=errors, page_obj=Paginator(qs.order_by(sort, "pk"), 9).get_page(request.GET.get("page")))
    elif page == "faq":
        context["regulations"] = Regulation.objects.filter(is_active=True, audience="public")
    return render(request, "public/page.html", context)
