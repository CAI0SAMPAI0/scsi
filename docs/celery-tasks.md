# Celery Tasks

## Configuração

- **Broker**: RabbitMQ
- **Result Backend**: Redis
- **Beat**: `django-celery-beat` (DatabaseScheduler)

## Tasks

| Task | Tipo | Descrição |
|---|---|---|
| `generate_client_summary` | sob demanda | Resumo IA do cliente |
| `generate_policy_summary` | sob demanda | Resumo IA da apólice |
| `generate_claim_summary` | sob demanda | Resumo IA do sinistro |
| `generate_proposal_summary` | sob demanda | Resumo IA da proposta |
| `generate_deal_summary` | sob demanda | Resumo IA da negociação |
| `send_async_email` | sob demanda | Envio de e-mails |
| `check_renewals_due` | Beat diária | Cria renovações |
| `expire_policies` | Beat diária | Marca apólices vencidas |
