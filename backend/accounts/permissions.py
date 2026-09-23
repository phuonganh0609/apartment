from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ALL = ("manager", "staff", "accountant")
OPERATIONS = ("manager", "staff")
FINANCE = ("manager", "accountant")


def allowed(user, roles=ALL):
    return (
        user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.role in roles)
    )


def require_roles(*roles):
    def decorate(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not allowed(request.user, roles):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapped

    return decorate


def deposit_allowed(user):
    return allowed(user, ("manager",)) or (
        allowed(user) and user.can_edit_deposit
    )


def navigation(request):
    user = request.user
    return {
        "can_operate": allowed(user, OPERATIONS),
        "can_finance": allowed(user, FINANCE),
        "can_manage": allowed(user, ("manager",)),
        "can_deposit": deposit_allowed(user),
    }
