import os
from datetime import date


def build_summary_prompt(entity_type, entity_data):
    """Build prompt for summary generation."""
    return f"""Você é o assistente inteligente de uma corretora de seguros.
Resuma os dados abaixo em Markdown com insights úteis.

Tipo de entidade: {entity_type}
Dados:
{entity_data}

Gere um resumo conciso com:
- Resumo executivo (2-3 linhas)
- Pontos-chave (bullet points)
- Ações recomendadas (se aplicável)

Data de hoje: {date.today().strftime('%d/%m/%Y')}
"""


def generate_summary_llm(entity_type, entity_data):
    """Generate summary using LLM (Groq via LangChain or direct)."""
    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage

        api_key = os.environ.get('GROQ_API_KEY', '')
        model_name = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')

        if not api_key:
            return generate_fallback_summary(entity_type, entity_data)

        llm = ChatGroq(model=model_name, groq_api_key=api_key)
        prompt = build_summary_prompt(entity_type, entity_data)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception:
        return generate_fallback_summary(entity_type, entity_data)


def generate_fallback_summary(entity_type, entity_data):
    """Generate a basic summary without LLM."""
    lines = [f'## Resumo do(a) {entity_type}\n']
    for key, value in entity_data.items():
        if value and key not in ('id', 'ai_summary', 'ai_summary_status'):
            lines.append(f'- **{key}**: {value}')
    lines.append('\n*Resumo gerado automaticamente.*')
    return '\n'.join(lines)


def summarize_entity(entity, entity_type, fetch_data_fn):
    """Common summary generation flow."""
    from django.utils import timezone

    entity.ai_summary_status = 'processing'
    entity.save(update_fields=['ai_summary_status'])

    try:
        data = fetch_data_fn(entity)
        summary = generate_summary_llm(entity_type, data)
        entity.ai_summary = summary
        entity.ai_summary_status = 'done'
        entity.ai_summary_updated_at = timezone.now()
        entity.save(update_fields=[
            'ai_summary', 'ai_summary_status', 'ai_summary_updated_at',
        ])
        return summary
    except Exception as e:
        entity.ai_summary_status = 'error'
        entity.save(update_fields=['ai_summary_status'])
        raise
