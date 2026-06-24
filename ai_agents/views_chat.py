import json
from django.http import JsonResponse, StreamingHttpResponse
from django.views import View
from django.views.generic import TemplateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from base.mixins import TenantQuerysetMixin
from ai_agents.models import ChatSession, ChatMessage
from ai_agents.tools import build_tenant_tools


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_agents/chat.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        if tenant:
            ctx['sessions'] = ChatSession.objects.filter(
                brokerage=tenant, user=self.request.user
            ).order_by('-created_at')
            session_id = self.request.GET.get('session')
            if session_id:
                ctx['session'] = ChatSession.objects.filter(
                    pk=session_id, brokerage=tenant, user=self.request.user
                ).first()
                if ctx['session']:
                    ctx['messages'] = ctx['session'].messages.all()
        return ctx


class ChatSessionCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        if not tenant:
            return JsonResponse({'ok': False}, status=400)
        session = ChatSession.objects.create(
            brokerage=tenant,
            user=request.user,
            title='Nova sessão',
        )
        return JsonResponse({'ok': True, 'session_id': session.pk, 'url': f'/ia/chat/?session={session.pk}'})


class ChatSessionDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        session = ChatSession.objects.filter(
            pk=kwargs['pk'], brokerage=request.tenant, user=request.user
        ).first()
        if session:
            session.delete()
        return JsonResponse({'ok': True})


class ChatMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        if not tenant:
            return JsonResponse({'ok': False}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

        session_id = data.get('session_id')
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'ok': False, 'error': 'Mensagem vazia'}, status=400)

        session = ChatSession.objects.filter(
            pk=session_id, brokerage=tenant, user=request.user
        ).first()
        if not session:
            return JsonResponse({'ok': False, 'error': 'Sessão não encontrada'}, status=404)

        ChatMessage.objects.create(
            brokerage=tenant,
            session=session,
            role=ChatMessage.Role.USER,
            content=content,
        )

        if session.title == 'Nova sessão':
            session.title = content[:50]
            session.save(update_fields=['title'])

        response_text = self._generate_response(tenant, session, content)

        ChatMessage.objects.create(
            brokerage=tenant,
            session=session,
            role=ChatMessage.Role.ASSISTANT,
            content=response_text,
        )

        return JsonResponse({'ok': True, 'response': response_text})

    def _generate_response(self, tenant, session, user_message):
        try:
            import os
            from langchain_groq import ChatGroq
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            api_key = os.environ.get('GROQ_API_KEY', '')
            model_name = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')

            if not api_key:
                return self._fallback_response(tenant, user_message)

            tools = build_tenant_tools(tenant)
            tools_desc = '\n'.join([
                f'- {name}: {fn.__doc__ or "Sem descrição"}'
                for name, fn in tools.items()
            ])

            system_msg = SystemMessage(content=f"""Você é o assistente da corretora "{tenant.trade_name or tenant.legal_name}".
Responda SEMPRE em português, em Markdown. Use as ferramentas disponíveis para consultar dados reais.
Ferramentas disponíveis:
{tools_desc}
NUNCA invente dados. Se a informação não existir, diga que não encontrou.
Data de hoje: {__import__('datetime').date.today().strftime('%d/%m/%Y')}.""")

            history = [system_msg]
            prev_messages = session.messages.order_by('created_at')[-10:]
            for msg in prev_messages:
                if msg.role == 'user':
                    history.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    history.append(AIMessage(content=msg.content))
            history.append(HumanMessage(content=user_message))

            llm = ChatGroq(model=model_name, groq_api_key=api_key)
            response = llm.invoke(history)
            return response.content
        except Exception:
            return self._fallback_response(tenant, user_message)

    def _fallback_response(self, tenant, user_message):
        tools = build_tenant_tools(tenant)
        lower_msg = user_message.lower()

        if any(w in lower_msg for w in ['cliente', 'clientes']):
            result = tools['list_clients']()
            if result:
                lines = [f'**{c["name"]}** ({c["document"]})' for c in result[:10]]
                return f'## Clientes encontrados\n\n' + '\n'.join(lines)
            return 'Nenhum cliente encontrado.'

        if any(w in lower_msg for w in ['apólice', 'aplices', 'apolice']):
            result = tools['list_policies']()
            if result:
                lines = [f'**{p["policy_number"]}** — {p["client"]} ({p["status"]})' for p in result[:10]]
                return f'## Apólices\n\n' + '\n'.join(lines)
            return 'Nenhuma apólice encontrada.'

        if any(w in lower_msg for w in ['renova', 'vencimento']):
            result = tools['list_renewals_due']()
            if result:
                lines = [f'**{r["policy_number"]}** — {r["client"]} (vence {r["due_date"]})' for r in result[:10]]
                return f'## Renovações pendentes\n\n' + '\n'.join(lines)
            return 'Nenhuma renovação pendente.'

        if any(w in lower_msg for w in ['comissão', 'comissoes', 'comissao']):
            result = tools['commissions_summary']()
            return f'## Resumo de Comissões\n\n- Total: R$ {result["total_commission"]}\n- Pendente: R$ {result["pending"]}\n- Recebido: R$ {result["received"]}'

        return f'Olá! Sou o assistente da corretora **{tenant.trade_name or tenant.legal_name}**. Posso ajudar com informações sobre clientes, apólices, renovações, comissões e mais. O que deseja saber?'
