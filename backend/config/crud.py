"""Shared, permission-checked server-rendered CRUD for small domain apps."""

from dataclasses import dataclass, field
from functools import reduce
from operator import or_

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.views.decorators.http import require_http_methods
from django.utils import formats
from datetime import date, datetime
from decimal import Decimal

from accounts.permissions import ALL, OPERATIONS, allowed, require_roles


@dataclass
class Resource:
    model: object
    form: object
    title: str
    namespace: str
    name: str
    columns: tuple
    search: tuple = ()
    filters: tuple = ()
    read_roles: tuple = ALL
    write_roles: tuple = OPERATIONS
    deletable: bool = True
    saver: object = None
    queryset: object = None
    form_options: object = None
    related: tuple = ()
    extra_context: object = None
    order_fields: tuple = ("pk",)

    def url(self, action, obj=None):
        return reverse(
            f"{self.namespace}:{self.name}_{action}",
            args=[obj.pk] if obj else [],
        )

    def template(self, action):
        return f"{self.namespace}/{self.name}_{action}.html"


def display(obj, name):
    for part in name.split("__"):
        if obj is None:
            return "—"
        getter = getattr(obj, f"get_{part}_display", None)
        obj = getter() if getter else getattr(obj, part, "—")
        if callable(obj):
            obj = obj()
    if isinstance(obj, bool):
        return "Có" if obj else "Không"
    if isinstance(obj, datetime):
        return formats.date_format(obj, "d/m/Y H:i")
    if isinstance(obj, date):
        return formats.date_format(obj, "d/m/Y")
    if isinstance(obj, Decimal):
        return formats.number_format(obj, use_l10n=True, force_grouping=True)
    return obj if obj is not None and obj != "" else "—"


def queryset_for(resource):
    qs = (
        resource.queryset()
        if resource.queryset
        else resource.model.objects.all()
    )
    if resource.related:
        qs = qs.select_related(*resource.related)
    return qs


def context_for(request, resource, obj=None):
    context = {
        "title": resource.title,
        "resource": resource,
        "list_url": resource.url("list"),
        "create_url": resource.url("create"),
        "can_write": allowed(request.user, resource.write_roles),
        "object": obj,
    }
    if obj:
        context.update(
            edit_url=resource.url("edit", obj),
            delete_url=(
                resource.url("delete", obj) if resource.deletable else None
            ),
        )
    if resource.extra_context:
        context.update(resource.extra_context(request, obj))
    return context


def resource_urls(resource, prefix=""):
    @require_roles(*resource.read_roles)
    def listing(request):
        qs = queryset_for(resource)
        query = request.GET.get("q", "").strip()[:200]
        if query and resource.search:
            qs = qs.filter(
                reduce(
                    or_,
                    [
                        Q(**{f"{key}__icontains": query})
                        for key in resource.search
                    ],
                )
            )
        filters = []
        for key, label, choices in resource.filters:
            options = list(choices() if callable(choices) else choices)
            selected = request.GET.get(key, "")
            if selected and selected in {str(v) for v, _ in options}:
                qs = qs.filter(**{key: selected})
            else:
                selected = ""
            filters.append(
                {
                    "key": key,
                    "label": label,
                    "options": options,
                    "selected": selected,
                }
            )
        sort = request.GET.get("sort", "-pk")
        if sort.lstrip("-") not in resource.order_fields:
            sort = "-pk"
        page = Paginator(qs.order_by(sort, "pk").distinct(), 12).get_page(
            request.GET.get("page")
        )
        rows = [
            {
                "object": obj,
                "cells": [display(obj, key) for key, _ in resource.columns],
                "url": resource.url("detail", obj),
            }
            for obj in page
        ]
        params = request.GET.copy()
        params.pop("page", None)
        context = context_for(request, resource)
        context.update(
            rows=rows,
            headers=[label for _, label in resource.columns],
            page_obj=page,
            query=query,
            filters=filters,
            sort=sort,
            query_string=params.urlencode(),
        )
        return render(
            request, [resource.template("list"), "generic/list.html"], context
        )

    @require_roles(*resource.read_roles)
    def detail(request, pk):
        obj = get_object_or_404(queryset_for(resource), pk=pk)
        context = context_for(request, resource, obj)
        context["fields"] = [
            (f.verbose_name, display(obj, f.name))
            for f in obj._meta.fields
            if f.name
            not in {
                "password",
                "last_login",
                "is_superuser",
                "is_staff",
                "file",
                "extracted_content",
            }
        ]
        return render(
            request,
            [resource.template("detail"), "generic/detail.html"],
            context,
        )

    @require_roles(*resource.write_roles)
    @require_http_methods(["GET", "POST"])
    def edit(request, pk=None):
        obj = get_object_or_404(queryset_for(resource), pk=pk) if pk else None
        options = (
            resource.form_options(request, obj)
            if resource.form_options
            else {}
        )
        form = resource.form(
            request.POST if request.method == "POST" else None,
            request.FILES or None,
            instance=obj,
            **options,
        )
        if request.method == "POST" and form.is_valid():
            try:
                with transaction.atomic():
                    item = form.save(commit=False)
                    if resource.saver:
                        resource.saver(item)
                    else:
                        item.full_clean()
                        item.save()
                    form.save_m2m()
                messages.success(request, "Đã lưu thông tin thành công.")
                return redirect(resource.url("detail", item))
            except ValidationError as exc:
                form.add_error(None, " ".join(exc.messages))
            except IntegrityError:
                form.add_error(
                    None,
                    (
                        "Dữ liệu trùng hoặc đã thay đổi. Vui "
                        "lòng kiểm tra và thử lại."
                    ),
                )
            except OperationalError:
                form.add_error(
                    None,
                    (
                        "Cơ sở dữ liệu đang bận hoặc chưa sẵn"
                        " sàng. Vui lòng thử lại sau."
                    ),
                )
        context = context_for(request, resource, obj)
        context.update(
            form=form,
            title=("Cập nhật " if obj else "Thêm ") + resource.title.lower(),
        )
        return render(
            request, [resource.template("form"), "generic/form.html"], context
        )

    @require_roles(*resource.write_roles)
    @require_http_methods(["GET", "POST"])
    def delete(request, pk):
        if not resource.deletable:
            raise Http404
        obj = get_object_or_404(queryset_for(resource), pk=pk)
        context = context_for(request, resource, obj)
        if request.method == "POST":
            try:
                with transaction.atomic():
                    obj.delete()
                messages.success(request, "Đã xóa thông tin.")
                return redirect(resource.url("list"))
            except ProtectedError:
                context["error"] = (
                    "Thông tin đang được hợp đồng hoặc dữ"
                    " liệu khác sử dụng nên không thể xóa"
                    "."
                )
        return render(request, "generic/delete.html", context)

    return [
        path(prefix, listing, name=f"{resource.name}_list"),
        path(prefix + "new/", edit, name=f"{resource.name}_create"),
        path(prefix + "<int:pk>/", detail, name=f"{resource.name}_detail"),
        path(prefix + "<int:pk>/edit/", edit, name=f"{resource.name}_edit"),
    ] + (
        [
            path(
                prefix + "<int:pk>/delete/",
                delete,
                name=f"{resource.name}_delete",
            )
        ]
        if resource.deletable
        else []
    )
