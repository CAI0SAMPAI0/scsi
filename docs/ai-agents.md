# Agentes de IA

## Tipos

| Tipo | Onde | Execução |
|---|---|---|
| **Summary Agent** | Botão "Resumir com IA" | Assíncrona (Celery) |
| **Chat Agent** | Tela de Chat IA | Síncrona |

## Isolamento

Tools recebem `brokerage` do servidor. O modelo nunca controla o tenant.

```python
def build_tenant_tools(brokerage):
    def list_clients(query=''):
        return Client.objects.filter(brokerage=brokerage)
    # ...
```

## Modelo

- **Groq** `llama-3.1-8b-instant` via `GROQ_API_KEY`
- Janela: últimas 10 mensagens por sessão
- Tools retornam dados compactos
