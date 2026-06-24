from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView

from tenants.forms import BrokerageOnboardingForm, BrokerageUpdateForm
from tenants.models import Brokerage, Plan


class BrokerageOnboardingView(LoginRequiredMixin, CreateView):
    template_name = 'tenants/onboarding.html'
    form_class = BrokerageOnboardingForm
    success_url = reverse_lazy('accounts:dashboard')

    def dispatch(self, request, *args, **kwargs):
        # Already has a brokerage
        if request.user.is_authenticated and request.user.brokerage_id:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plans'] = Plan.objects.filter(is_available=True)
        return ctx

    def form_valid(self, form):
        # Get free plan by default
        free_plan = Plan.objects.filter(slug='free').first()
        brokerage = form.save(commit=False)
        brokerage.owner = self.request.user
        brokerage.plan = free_plan
        brokerage.save()

        # Attach user to brokerage and set role as owner
        self.request.user.brokerage = brokerage
        self.request.user.role = 'owner'
        self.request.user.save()

        messages.success(self.request, f'Corretora "{brokerage}" cadastrada com sucesso!')
        return redirect(self.success_url)


class BrokerageUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'tenants/brokerage_form.html'
    form_class = BrokerageUpdateForm
    success_url = reverse_lazy('tenants:my_plan')

    def get_object(self):
        return self.request.tenant

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.tenant:
            return redirect('tenants:onboarding')
        if request.user.role not in ('owner',):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Dados da corretora atualizados.')
        return super().form_valid(form)


class MyPlanView(LoginRequiredMixin, TemplateView):
    template_name = 'tenants/my_plan.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.tenant:
            return redirect('tenants:onboarding')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        brokerage = self.request.tenant
        ctx['brokerage'] = brokerage
        ctx['plan'] = brokerage.plan
        ctx['available_plans'] = Plan.objects.filter(is_available=True)
        ctx['member_count'] = brokerage.members.count()
        return ctx
