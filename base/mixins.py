from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class TenantQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.tenant:
            return qs.none()
        return qs.filter(brokerage=self.request.tenant)


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.tenant:
            from django.shortcuts import redirect
            return redirect('tenants:onboarding')
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
