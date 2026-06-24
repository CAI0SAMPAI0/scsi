from django.db.models import Count, Sum
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin
from crm.models import Pipeline, Stage, Deal, DealStageHistory
from crm.forms import PipelineForm, StageForm, DealForm


class PipelineListView(TenantQuerysetMixin, RoleRequiredMixin, ListView):
    model = Pipeline
    template_name = 'crm/pipeline_list.html'
    context_object_name = 'pipelines'
    allowed_roles = ('owner', 'manager')


class PipelineCreateView(TenantQuerysetMixin, RoleRequiredMixin, CreateView):
    model = Pipeline
    form_class = PipelineForm
    template_name = 'crm/pipeline_form.html'
    success_url = '/crm/pipelines/'
    allowed_roles = ('owner', 'manager')

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        return super().form_valid(form)


class PipelineUpdateView(TenantQuerysetMixin, RoleRequiredMixin, UpdateView):
    model = Pipeline
    form_class = PipelineForm
    template_name = 'crm/pipeline_form.html'
    success_url = '/crm/pipelines/'
    allowed_roles = ('owner', 'manager')


class StageCreateView(TenantQuerysetMixin, RoleRequiredMixin, CreateView):
    model = Stage
    form_class = StageForm
    template_name = 'crm/stage_form.html'
    allowed_roles = ('owner', 'manager')

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        return super().form_valid(form)

    def get_success_url(self):
        return f'/crm/pipelines/{self.object.pipeline.pk}/'


class StageUpdateView(TenantQuerysetMixin, RoleRequiredMixin, UpdateView):
    model = Stage
    form_class = StageForm
    template_name = 'crm/stage_form.html'
    allowed_roles = ('owner', 'manager')

    def get_success_url(self):
        return f'/crm/pipelines/{self.object.pipeline.pk}/'


class KanbanView(TenantQuerysetMixin, TemplateView):
    template_name = 'crm/kanban.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        pipeline_id = self.request.GET.get('pipeline')
        pipelines = Pipeline.objects.filter(brokerage=tenant)
        pipeline = pipelines.filter(pk=pipeline_id).first() if pipeline_id else pipelines.filter(is_default=True).first()
        if not pipeline:
            pipeline = pipelines.first()

        stages = []
        if pipeline:
            for stage in pipeline.stages.all():
                deals = Deal.objects.filter(
                    brokerage=tenant, pipeline=pipeline, stage=stage
                ).select_related('client', 'producer', 'line_of_business')
                stages.append({
                    'stage': stage,
                    'deals': deals,
                    'count': deals.count(),
                    'total_value': deals.aggregate(total=Sum('estimated_value'))['total'] or 0,
                })

        ctx['pipeline'] = pipeline
        ctx['pipelines'] = pipelines
        ctx['stages'] = stages
        return ctx


class DealUpdateStageView(TenantQuerysetMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ('owner', 'manager', 'broker')

    def post(self, request, *args, **kwargs):
        import json
        try:
            data = json.loads(request.body)
            deal_id = data.get('deal_id')
            stage_id = data.get('stage_id')

            deal = Deal.objects.get(pk=deal_id, brokerage=request.tenant)
            old_stage = deal.stage
            new_stage = Stage.objects.get(pk=stage_id, brokerage=request.tenant)

            deal.stage = new_stage
            if new_stage.is_won:
                deal.status = Deal.Status.WON
            elif new_stage.is_lost:
                deal.status = Deal.Status.LOST
            deal.save(update_fields=['stage', 'status', 'updated_at'])

            DealStageHistory.objects.create(
                brokerage=request.tenant,
                deal=deal,
                from_stage=old_stage,
                to_stage=new_stage,
                changed_by=request.user,
            )

            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


class DealListView(TenantQuerysetMixin, ListView):
    model = Deal
    template_name = 'crm/deal_list.html'
    context_object_name = 'deals'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('client', 'producer', 'stage', 'line_of_business')
        status = self.request.GET.get('status')
        pipeline_id = self.request.GET.get('pipeline')
        if status:
            qs = qs.filter(status=status)
        if pipeline_id:
            qs = qs.filter(pipeline_id=pipeline_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pipelines'] = Pipeline.objects.filter(brokerage=self.request.tenant)
        return ctx


class DealCreateView(TenantQuerysetMixin, RoleRequiredMixin, CreateView):
    model = Deal
    form_class = DealForm
    template_name = 'crm/deal_form.html'
    allowed_roles = ('owner', 'manager', 'broker')
    success_url = '/crm/negociacoes/'

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        if not form.instance.pipeline:
            form.instance.pipeline = Pipeline.objects.filter(
                brokerage=self.request.tenant, is_default=True
            ).first()
        if not form.instance.stage:
            form.instance.stage = Stage.objects.filter(
                brokerage=self.request.tenant, pipeline=form.instance.pipeline
            ).order_by('order').first()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs


class DealUpdateView(TenantQuerysetMixin, RoleRequiredMixin, UpdateView):
    model = Deal
    form_class = DealForm
    template_name = 'crm/deal_form.html'
    allowed_roles = ('owner', 'manager', 'broker')
    success_url = '/crm/negociacoes/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        return kwargs


class DealDetailView(TenantQuerysetMixin, DetailView):
    model = Deal
    template_name = 'crm/deal_detail.html'
    context_object_name = 'deal'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['history'] = self.get_object().stage_history.select_related(
            'from_stage', 'to_stage', 'changed_by'
        )
        return ctx
