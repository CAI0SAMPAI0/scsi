# Permissões

## Roles

| Role | Pode | Não pode |
|---|---|---|
| `owner` | Tudo no tenant | Acessar outra corretora |
| `manager` | Gerenciar equipe, CRM, relatórios | Alterar plano |
| `broker` | Criar/editar clientes, propostas, apólices | Gerenciar usuários |
| `agent` | Operar negócios vinculados | Configurações |
| `producer` | Criar negociações próprias | Dados de outros |
| `operational` | Anexos, endossos, cadastros | Excluir entidades críticas |

## Mecanismos

- `LoginRequiredMixin` em todas as CBVs internas
- `TenantQuerysetMixin` filtra por `request.tenant`
- `RoleRequiredMixin` valida `user.role`
- Forms com querysets filtrados por tenant
