from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from commissions.models import Commission, CommissionSplit
from commissions.forms import CommissionSplitForm


class CommissionListView(TenantQuerysetMixin, ListView):
    model = Commission
    template_name = 'commissions/commission_list.html'
    context_object_name = 'commissions'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('policy').order_by('-reference_date')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        ctx['total_received'] = Commission.objects.filter(
            brokerage=tenant, status__in=['received', 'paid']
        ).aggregate(total=Sum('insurer_amount'))['total'] or 0
        ctx['total_pending'] = Commission.objects.filter(
            brokerage=tenant, status='pending'
        ).aggregate(total=Sum('insurer_amount'))['total'] or 0
        return ctx


class CommissionDetailView(TenantQuerysetMixin, RoleRequiredMixin, DetailView):
    model = Commission
    template_name = 'commissions/commission_detail.html'
    context_object_name = 'commission'
    allowed_roles = ('owner', 'manager')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        commission = self.get_object()
        ctx['splits'] = commission.splits.select_related('agent', 'producer')
        ctx['split_form'] = CommissionSplitForm(brokerage=self.request.tenant)
        ctx['split_total'] = commission.splits.aggregate(total=Sum('amount'))['total'] or 0
        return ctx


class CommissionSplitCreateView(TenantQuerysetMixin, RoleRequiredMixin, CreateView):
    model = CommissionSplit
    form_class = CommissionSplitForm
    allowed_roles = ('owner', 'manager')

    def form_valid(self, form):
        commission = Commission.objects.get(
            pk=self.kwargs['commission_pk'],
            brokerage=self.request.tenant,
        )
        form.instance.commission = commission
        form.instance.brokerage = self.request.tenant
        messages.success(self.request, 'Repasse adicionado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'commissions:commission_detail',
            kwargs={'pk': self.kwargs['commission_pk']},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs
