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


# ── Dashboard placeholder ─────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.tenant:
            return redirect('tenants:onboarding')
        return super().dispatch(request, *args, **kwargs)


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
