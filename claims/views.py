from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from claims.models import Claim, Endorsement
from claims.forms import ClaimForm, ClaimSearchForm, EndorsementForm
from insurance.models import Policy

ROLES = ('owner', 'manager', 'broker', 'agent', 'producer')


class ClaimListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Claim
    template_name = 'claims/claim_list.html'
    context_object_name = 'claims'
    paginate_by = 25
    allowed_roles = ROLES

    def get_queryset(self):
        qs = super().get_queryset().select_related('policy', 'covered_item')
        form = ClaimSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            status = form.cleaned_data.get('status', '')
            if q:
                qs = qs.filter(
                    Q(claim_number__icontains=q)
                    | Q(policy__policy_number__icontains=q)
                )
            if status:
                qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = ClaimSearchForm(self.request.GET or None)
        return ctx


class ClaimCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'claims/claim_form.html'
    success_url = reverse_lazy('claims:claim_list')
    allowed_roles = ROLES

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        policy_id = self.kwargs.get('policy_id')
        if policy_id:
            initial['policy'] = policy_id
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Sinistro criado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['policy_id'] = self.kwargs.get('policy_id')
        return ctx


class ClaimUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'claims/claim_form.html'
    success_url = reverse_lazy('claims:claim_list')
    allowed_roles = ROLES

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Sinistro atualizado com sucesso.')
        return super().form_valid(form)


class ClaimDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    model = Claim
    template_name = 'claims/claim_detail.html'
    context_object_name = 'claim'
    allowed_roles = ROLES

    def get_queryset(self):
        return super().get_queryset().select_related('policy', 'covered_item')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab', 'info')
        ctx['active_tab'] = tab
        if tab == 'attachments':
            from documents.models import Document
            ct = ContentType.objects.get_for_model(self.object)
            ctx['content_type_id'] = ct.pk
            ctx['documents'] = Document.objects.filter(
                content_type=ct, object_id=self.object.pk,
            )
        return ctx


class EndorsementListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Endorsement
    template_name = 'claims/endorsement_list.html'
    context_object_name = 'endorsements'
    paginate_by = 25
    allowed_roles = ROLES

    def get_queryset(self):
        self.policy = get_object_or_404(
            Policy.objects.filter(brokerage=self.request.tenant),
            pk=self.kwargs['policy_id'],
        )
        return super().get_queryset().filter(policy=self.policy)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['policy'] = self.policy
        return ctx


class EndorsementCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Endorsement
    form_class = EndorsementForm
    template_name = 'claims/endorsement_form.html'
    allowed_roles = ROLES

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        self.policy = get_object_or_404(
            Policy.objects.filter(brokerage=self.request.tenant),
            pk=self.kwargs['policy_id'],
        )
        form.instance.policy = self.policy
        messages.success(self.request, 'Endosso criado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('claims:endorsement_list', kwargs={'policy_id': self.kwargs['policy_id']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['policy'] = get_object_or_404(
            Policy.objects.filter(brokerage=self.request.tenant),
            pk=self.kwargs['policy_id'],
        )
        return ctx
