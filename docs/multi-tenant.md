# Multi Tenant

## Estratégia: Shared Schema por FK

O SCSI usa **multi tenancy compartilhada** — um único banco, um único schema, isolamento por `brokerage` FK.

## Defesa em Camadas

1. **Model**: `TenantAwareModel` com `brokerage` FK
2. **Middleware**: `request.tenant = user.brokerage`
3. **Manager**: `TenantManager.for_tenant()`
4. **Mixin**: `TenantQuerysetMixin` filtra `get_queryset()`
5. **Forms**: querysets filtrados por tenant
6. **Validação**: `clean()`/`save()` valida FKs do mesmo tenant
7. **IA**: tools recebem `brokerage` do servidor

## Regras

- Nunca retornar dados sem filtro de tenant
- Objetos de outro tenant retornam 404 (nunca 403)
- `request.tenant` disponível desde o middleware
