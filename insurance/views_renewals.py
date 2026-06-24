from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from insurance.models import Renewal


class RenewalListView(TenantQuerysetMixin, ListView):
    model = Renewal
    template_name = 'insurance/renewal_list.html'
    context_object_name = 'renewals'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('policy', 'policy__client', 'new_policy')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class RenewalDetailView(TenantQuerysetMixin, RoleRequiredMixin, DetailView):
    model = Renewal
    template_name = 'insurance/renewal_detail.html'
    context_object_name = 'renewal'
    allowed_roles = ('owner', 'manager', 'broker')


class RenewalUpdateView(TenantQuerysetMixin, RoleRequiredMixin, UpdateView):
    model = Renewal
    template_name = 'insurance/renewal_form.html'
    fields = ['status', 'notes']
    success_url = reverse_lazy('insurance:renewal_list')
    allowed_roles = ('owner', 'manager', 'broker')

    def form_valid(self, form):
        messages.success(self.request, 'Renovação atualizada com sucesso.')
        return super().form_valid(form)
