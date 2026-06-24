from django.contrib import messages
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from insurance.models import Proposal, Policy, CoveredItem
from insurance.forms import (
    ProposalForm, ProposalSearchForm,
    PolicySearchForm,
    CoveredItemForm, GeneratePolicyForm,
)

ROLES = ('owner', 'manager', 'broker', 'agent', 'producer')

CoveredItemFormSet = inlineformset_factory(
    Proposal, CoveredItem, form=CoveredItemForm,
    extra=1, can_delete=True,
)


# ── Proposal views ──────────────────────────────────────────────


class ProposalListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Proposal
    template_name = 'insurance/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 25
    allowed_roles = ROLES

    def get_queryset(self):
        qs = super().get_queryset().select_related('client', 'insurer', 'line_of_business')
        form = ProposalSearchForm(self.request.GET, brokerage=self.request.tenant)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            status = form.cleaned_data.get('status', '')
            insurer = form.cleaned_data.get('insurer')
            lob = form.cleaned_data.get('line_of_business')
            if q:
                qs = qs.filter(
                    Q(number__icontains=q)
                    | Q(client__name__icontains=q)
                    | Q(insurer__name__icontains=q)
                )
            if status:
                qs = qs.filter(status=status)
            if insurer:
                qs = qs.filter(insurer=insurer)
            if lob:
                qs = qs.filter(line_of_business=lob)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = ProposalSearchForm(self.request.GET or None, brokerage=self.request.tenant)
        return ctx


class ProposalCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'insurance/proposal_form.html'
    success_url = reverse_lazy('insurance:proposal_list')
    allowed_roles = ROLES

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['item_formset'] = CoveredItemFormSet(
                self.request.POST, prefix='items',
            )
        else:
            ctx['item_formset'] = CoveredItemFormSet(prefix='items')
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        item_formset = ctx['item_formset']
        if item_formset.is_valid():
            self.object = form.save()
            item_formset.instance = self.object
            item_formset.save()
            messages.success(self.request, f'Proposta "{self.object.number}" criada com sucesso.')
            return redirect(self.get_success_url())
        return self.render_to_response(ctx)


class ProposalUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'insurance/proposal_form.html'
    success_url = reverse_lazy('insurance:proposal_list')
    allowed_roles = ROLES

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['item_formset'] = CoveredItemFormSet(
                self.request.POST, instance=self.object, prefix='items',
            )
        else:
            ctx['item_formset'] = CoveredItemFormSet(
                instance=self.object, prefix='items',
            )
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        item_formset = ctx['item_formset']
        if item_formset.is_valid():
            self.object = form.save()
            item_formset.save()
            messages.success(self.request, f'Proposta "{self.object.number}" atualizada com sucesso.')
            return redirect(self.get_success_url())
        return self.render_to_response(ctx)


class ProposalDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    model = Proposal
    template_name = 'insurance/proposal_detail.html'
    context_object_name = 'proposal'
    allowed_roles = ROLES

    def get_queryset(self):
        return super().get_queryset().select_related('client', 'insurer', 'line_of_business', 'producer', 'agent')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = self.request.GET.get('tab', 'info')
        ctx['covered_items'] = self.object.covered_items.all()
        ctx['generate_form'] = GeneratePolicyForm()

        from django.contrib.contenttypes.models import ContentType
        from documents.models import Document
        ct = ContentType.objects.get_for_model(Proposal)
        ctx['content_type_id'] = ct.pk
        ctx['documents'] = Document.objects.filter(
            brokerage=self.request.tenant,
            content_type=ct,
            object_id=self.object.pk,
        )
        return ctx


class GeneratePolicyFromProposalView(RoleRequiredMixin, TenantQuerysetMixin, View):
    model = Proposal
    allowed_roles = ROLES

    def post(self, request, pk):
        proposal = get_object_or_404(
            Proposal.objects.filter(brokerage=request.tenant), pk=pk,
        )
        form = GeneratePolicyForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Número da apólice é obrigatório.')
            return redirect('insurance:proposal_detail', pk=pk)

        if proposal.status == 'converted':
            messages.warning(request, 'Esta proposta já foi convertida em apólice.')
            return redirect('insurance:proposal_detail', pk=pk)

        from insurance.services import generate_policy_from_proposal
        try:
            policy = generate_policy_from_proposal(
                proposal=proposal,
                policy_number=form.cleaned_data['policy_number'],
                brokerage=request.tenant,
            )
            messages.success(request, f'Apólice "{policy.policy_number}" gerada com sucesso.')
            return redirect('insurance_policies:policy_detail', pk=policy.pk)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('insurance:proposal_detail', pk=pk)


# ── Policy views ────────────────────────────────────────────────


class PolicyListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    model = Policy
    template_name = 'insurance/policy_list.html'
    context_object_name = 'policies'
    paginate_by = 25
    allowed_roles = ROLES

    def get_queryset(self):
        qs = super().get_queryset().select_related('client', 'insurer', 'line_of_business')
        form = PolicySearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '').strip()
            status = form.cleaned_data.get('status', '')
            if q:
                qs = qs.filter(
                    Q(policy_number__icontains=q)
                    | Q(client__name__icontains=q)
                )
            if status:
                qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = PolicySearchForm(self.request.GET or None)
        return ctx


class PolicyDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    model = Policy
    template_name = 'insurance/policy_detail.html'
    context_object_name = 'policy'
    allowed_roles = ROLES

    def get_queryset(self):
        return super().get_queryset().select_related(
            'client', 'insurer', 'line_of_business', 'producer', 'agent', 'proposal',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = self.request.GET.get('tab', 'info')
        ctx['covered_items'] = self.object.covered_items.all()

        from django.contrib.contenttypes.models import ContentType
        from documents.models import Document
        ct = ContentType.objects.get_for_model(Policy)
        ctx['content_type_id'] = ct.pk
        ctx['documents'] = Document.objects.filter(
            brokerage=self.request.tenant,
            content_type=ct,
            object_id=self.object.pk,
        )
        return ctx
