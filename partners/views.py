from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from partners.models import Agent, Producer
from partners.forms import AgentForm, AgentSearchForm, ProducerForm, ProducerSearchForm


class AgentListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Agent
    template_name = 'partners/agent_list.html'
    context_object_name = 'agents'
    paginate_by = 25
    allowed_roles = ('owner', 'manager', 'broker')

    def get_queryset(self):
        qs = super().get_queryset()
        form = AgentSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(name__icontains=q) | Q(document__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = AgentSearchForm(self.request.GET or None)
        return ctx


class AgentCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Agent
    form_class = AgentForm
    template_name = 'partners/agent_form.html'
    success_url = reverse_lazy('partners:agent_list')
    allowed_roles = ('owner', 'manager', 'broker')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Agente "{form.instance.name}" cadastrado com sucesso.')
        return super().form_valid(form)


class AgentUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'partners/agent_form.html'
    success_url = reverse_lazy('partners:agent_list')
    allowed_roles = ('owner', 'manager', 'broker')

    def get_queryset(self):
        return super().get_queryset()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Agente "{form.instance.name}" atualizado com sucesso.')
        return super().form_valid(form)


class ProducerListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Producer
    template_name = 'partners/producer_list.html'
    context_object_name = 'producers'
    paginate_by = 25
    allowed_roles = ('owner', 'manager', 'broker')

    def get_queryset(self):
        qs = super().get_queryset().select_related('agent')
        form = ProducerSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(name__icontains=q) | Q(document__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = ProducerSearchForm(self.request.GET or None)
        return ctx


class ProducerCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'partners/producer_form.html'
    success_url = reverse_lazy('partners:producer_list')
    allowed_roles = ('owner', 'manager', 'broker')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Produtor "{form.instance.name}" cadastrado com sucesso.')
        return super().form_valid(form)


class ProducerUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'partners/producer_form.html'
    success_url = reverse_lazy('partners:producer_list')
    allowed_roles = ('owner', 'manager', 'broker')

    def get_queryset(self):
        return super().get_queryset()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Produtor "{form.instance.name}" atualizado com sucesso.')
        return super().form_valid(form)
