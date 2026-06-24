from base.managers import current_tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = None
        if (
            request.user.is_authenticated
            and hasattr(request.user, 'brokerage_id')
            and request.user.brokerage_id
        ):
            tenant = request.user.brokerage
        request.tenant = tenant
        token = current_tenant.set(tenant)
        try:
            response = self.get_response(request)
        finally:
            current_tenant.reset(token)
        return response
