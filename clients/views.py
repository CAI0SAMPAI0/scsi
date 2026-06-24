from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from clients.models import Client
from clients.forms import ClientForm, ClientSearchForm


class ClientListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 25
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer')

    def get_queryset(self):
        qs = super().get_queryset().select_related('brokerage')
        form = ClientSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            person_type = form.cleaned_data.get('person_type', '')
            if q:
                qs = qs.filter(
                    models.Q(name__icontains=q)
                    | models.Q(document__icontains=q)
                    | models.Q(email__icontains=q)
                )
            if person_type:
                qs = qs.filter(person_type=person_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = ClientSearchForm(self.request.GET or None)
        return ctx


class ClientCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.name}" cadastrado com sucesso.')
        return super().form_valid(form)


class ClientUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    allowed_roles = ('owner', 'manager', 'broker', 'agent')

    def get_queryset(self):
        return super().get_queryset()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.name}" atualizado com sucesso.')
        return super().form_valid(form)


class ClientDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = self.request.GET.get('tab', 'info')
        return ctx
