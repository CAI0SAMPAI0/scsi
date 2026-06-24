from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, TemplateView, View

from accounts.forms import (
    EmailLoginForm,
    RegisterForm,
    ProfileForm,
    MemberCreateForm,
    MemberUpdateForm,
)
from accounts.models import User
from base.mixins import RoleRequiredMixin


# ── Authentication ────────────────────────────────────────────────────────────

class EmailLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = EmailLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('tenants:onboarding')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='accounts.backends.EmailBackend')
        messages.success(self.request, 'Conta criada com sucesso! Configure sua corretora.')
        return redirect(self.success_url)


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso.')
        return super().form_valid(form)


# ── Dashboard ─────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.tenant:
            return redirect('tenants:onboarding')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import Count, Sum
        from django.db.models.functions import TruncMonth
        from datetime import date, timedelta
        from clients.models import Client
        from insurance.models import Policy, Proposal, Renewal
        from claims.models import Claim
        from commissions.models import Commission
        from crm.models import Deal
        import calendar

        tenant = self.request.tenant
        today = date.today()
        thirty_days = today - timedelta(days=30)

        ctx['client_count'] = Client.objects.filter(brokerage=tenant, is_active=True).count()
        ctx['policy_count'] = Policy.objects.filter(brokerage=tenant, status='active').count()
        ctx['proposal_count'] = Proposal.objects.filter(brokerage=tenant).exclude(status='converted').count()
        ctx['claim_count'] = Claim.objects.filter(brokerage=tenant).exclude(status='closed').count()

        renewals_30 = Renewal.objects.filter(
            brokerage=tenant, status='pending',
            due_date__lte=today + timedelta(days=30),
        )
        ctx['renewal_count'] = renewals_30.count()

        total_commission = Commission.objects.filter(
            brokerage=tenant, status__in=['received', 'paid'],
        ).aggregate(total=Sum('insurer_amount'))['total'] or 0
        ctx['total_commission'] = total_commission

        # CRM Funnel
        pipeline = Deal.objects.filter(brokerage=tenant).values('stage__name', 'stage__color').annotate(
            count=Count('id'), total=Sum('estimated_value')
        ).order_by('stage__order')
        funnel_list = list(pipeline)
        for f in funnel_list:
            f['total'] = f['total'] or 0
        ctx['funnel_data'] = funnel_list

        # Policies by line of business with colors
        lob_colors = ['#3454d1', '#17c666', '#f5a623', '#ea4d4d', '#9b59b6', '#00bcd4']
        policies_by_lob = list(Policy.objects.filter(
            brokerage=tenant, status='active',
        ).values('line_of_business__name').annotate(
            count=Count('id')
        ).order_by('-count')[:6])
        for i, lob in enumerate(policies_by_lob):
            lob['color'] = lob_colors[i % len(lob_colors)]
        ctx['policies_by_lob'] = policies_by_lob

        # Top insurers with colors
        insurer_colors = ['#3454d1', '#17c666', '#f5a623', '#ea4d4d', '#9b59b6']
        top_insurers = list(Policy.objects.filter(
            brokerage=tenant, status='active',
        ).values('insurer__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5])
        for i, ins in enumerate(top_insurers):
            ins['color'] = insurer_colors[i % len(insurer_colors)]
        ctx['top_insurers'] = top_insurers

        # Claims by status with colors
        status_colors = {
            'opened': '#ea4d4d', 'under_analysis': '#f5a623',
            'approved': '#17c666', 'denied': '#6c757d',
            'paid': '#3454d1', 'closed': '#adb5bd',
        }
        claims_by_status = list(Claim.objects.filter(
            brokerage=tenant,
        ).values('status').annotate(count=Count('id')))
        for cs in claims_by_status:
            cs['color'] = status_colors.get(cs['status'], '#6c757d')
        ctx['claims_by_status'] = claims_by_status

        # Monthly production (last 6 months)
        monthly_qs = Policy.objects.filter(
            brokerage=tenant, start_date__isnull=False,
        ).annotate(
            month=TruncMonth('start_date'),
        ).values('month').annotate(
            premium=Sum('total_premium'),
            commission=Sum('total_premium'),
        ).order_by('month')
        monthly = list(monthly_qs)[-6:]

        for m in monthly:
            m['label'] = m['month'].strftime('%b/%Y')
            m['premium'] = float(m['premium'] or 0)
            m['commission'] = float(m['commission'] or 0) * 0.15

        premiums = [m['premium'] for m in monthly]
        commissions = [m['commission'] for m in monthly]
        ctx['monthly_data'] = monthly
        ctx['max_premium'] = max(premiums) if premiums else 1
        ctx['max_commission'] = max(commissions) if commissions else 1

        return ctx


# ── Members (Sprints 7) ───────────────────────────────────────────────────────

class MemberListView(RoleRequiredMixin, ListView):
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'
    allowed_roles = ('owner', 'manager')

    def get_queryset(self):
        return User.objects.filter(brokerage=self.request.tenant).order_by('first_name')


class MemberCreateView(RoleRequiredMixin, CreateView):
    template_name = 'accounts/member_form.html'
    form_class = MemberCreateForm
    success_url = reverse_lazy('accounts:member_list')
    allowed_roles = ('owner', 'manager')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Membro adicionado com sucesso.')
        return super().form_valid(form)


class MemberUpdateView(RoleRequiredMixin, UpdateView):
    template_name = 'accounts/member_form.html'
    form_class = MemberUpdateForm
    success_url = reverse_lazy('accounts:member_list')
    allowed_roles = ('owner', 'manager')

    def get_queryset(self):
        return User.objects.filter(brokerage=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, 'Membro atualizado com sucesso.')
        return super().form_valid(form)
