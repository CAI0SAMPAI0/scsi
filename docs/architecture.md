# Arquitetura

## Visão de Camadas

```mermaid
graph TB
    subgraph "Frontend"
        LP[Landing Page]
        AUTH[Login/Registro]
        DASH[Dashboard]
        CRUDS[CRUDs]
        CRM[CRM Kanban]
        CHAT[Chat IA]
    end

    subgraph "Backend Django"
        URLS[URL Router]
        MW[Middlewares]
        VIEWS[CBVs + Mixins]
        MODELS[Models/ORM]
    end

    subgraph "IA"
        SUMM[Summary Agents]
        CHATAG[Chat Agent]
        TOOLS[Tenant Tools]
    end

    subgraph "Async Celery"
        BROKER[RabbitMQ]
        WORKER[Worker]
        BEAT[Beat]
    end

    subgraph "Data"
        DB[(PostgreSQL)]
        MEDIA[Media Protegida]
    end

    LP --> URLS
    URLS --> MW
    MW --> VIEWS
    VIEWS --> MODELS
    MODELS --> DB
    CHATAG --> TOOLS
    TOOLS --> MODELS
    WORKER --> BROKER
```

## Princípios

- **Monolito modular Django** — apps coesas por responsabilidade
- **Thin views, fat services** — lógica em `services.py`
- **Tenant em primeiro lugar** — `TenantMiddleware` resolve `request.tenant`
- **Assíncrono por padrão** — Celery para tarefas pesadas
