from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from insurers.models import Insurer, LineOfBusiness
from insurers.forms import (
    InsurerForm, InsurerSearchForm,
    LineOfBusinessForm, LineOfBusinessSearchForm,
)


class InsurerListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Insurer
    template_name = 'insurers/insurer_list.html'
    context_object_name = 'insurers'
    paginate_by = 25
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_queryset(self):
        qs = super().get_queryset()
        form = InsurerSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(name__icontains=q)
                    | Q(cnpj__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = InsurerSearchForm(self.request.GET or None)
        return ctx


class InsurerCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:insurer_list')
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Seguradora "{form.instance.name}" cadastrada com sucesso.')
        return super().form_valid(form)


class InsurerUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:insurer_list')
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Seguradora "{form.instance.name}" atualizada com sucesso.')
        return super().form_valid(form)


class LineOfBusinessListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = LineOfBusiness
    template_name = 'insurers/lob_list.html'
    context_object_name = 'lobs'
    paginate_by = 25
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_queryset(self):
        qs = super().get_queryset()
        form = LineOfBusinessSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            category = form.cleaned_data.get('category', '')
            if q:
                qs = qs.filter(name__icontains=q)
            if category:
                qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = LineOfBusinessSearchForm(self.request.GET or None)
        return ctx


class LineOfBusinessCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = LineOfBusiness
    form_class = LineOfBusinessForm
    template_name = 'insurers/lob_form.html'
    success_url = reverse_lazy('insurers:lob_list')
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Ramo "{form.instance.name}" cadastrado com sucesso.')
        return super().form_valid(form)


class LineOfBusinessUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = LineOfBusiness
    form_class = LineOfBusinessForm
    template_name = 'insurers/lob_form.html'
    success_url = reverse_lazy('insurers:lob_list')
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Ramo "{form.instance.name}" atualizado com sucesso.')
        return super().form_valid(form)
