from .models import Regulation


def visible_regulations(user, queryset=None):
    queryset = Regulation.objects.all() if queryset is None else queryset
    if not user.is_authenticated or not user.is_active:
        return queryset.none()
    if user.is_superuser or user.role == "manager":
        return queryset
    scopes = {"tenant": ["public", "tenants"], "staff": ["public", "tenants", "internal"],
              "accountant": ["public", "tenants", "finance"]}
    return queryset.filter(audience__in=scopes.get(user.role, []))
