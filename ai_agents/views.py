from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from base.mixins import TenantQuerysetMixin


class TriggerSummaryView(LoginRequiredMixin, View):
    """Generic view to trigger AI summary for any entity."""

    ENTITY_MAP = {
        'client': ('clients.models', 'Client', 'ai_agents.tasks.generate_client_summary'),
        'policy': ('insurance.models', 'Policy', 'ai_agents.tasks.generate_policy_summary'),
        'claim': ('claims.models', 'Claim', 'ai_agents.tasks.generate_claim_summary'),
        'proposal': ('insurance.models', 'Proposal', 'ai_agents.tasks.generate_proposal_summary'),
        'deal': ('crm.models', 'Deal', 'ai_agents.tasks.generate_deal_summary'),
    }

    def post(self, request, *args, **kwargs):
        entity_type = kwargs.get('entity_type')
        entity_id = kwargs.get('entity_id')

        if entity_type not in self.ENTITY_MAP:
            return JsonResponse({'ok': False, 'error': 'Tipo inválido'}, status=400)

        module_path, model_name, task_path = self.ENTITY_MAP[entity_type]
        import importlib
        module = importlib.import_module(module_path)
        model = getattr(module, model_name)

        try:
            entity = model.objects.get(pk=entity_id, brokerage=request.tenant)
        except model.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Não encontrado'}, status=404)

        if entity.ai_summary_status == 'processing':
            return JsonResponse({'ok': False, 'error': 'Já está processando'}, status=400)

        entity.ai_summary_status = 'processing'
        entity.save(update_fields=['ai_summary_status'])

        task_module, task_name = task_path.rsplit('.', 1)
        mod = importlib.import_module(task_module)
        task_fn = getattr(mod, task_name)
        task_fn.delay(entity.pk)

        messages.success(request, 'Estamos gerando o resumo. Você será notificado quando ficar pronto.')
        return JsonResponse({'ok': True})
