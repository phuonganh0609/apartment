from contextvars import ContextVar

audit_actor = ContextVar("audit_actor", default="")


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = audit_actor.set(request.user.username if request.user.is_authenticated else "")
        try:
            return self.get_response(request)
        finally:
            audit_actor.reset(token)
