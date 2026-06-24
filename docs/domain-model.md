# Modelo de Domínio

## Entidades Principais

### Core
- **Brokerage** — o tenant (corretora)
- **User** — login por email, role, brokerage FK
- **Plan** / **Subscription** — planos e assinaturas

### Operação
- **Client** — clientes PF/PJ
- **Insurer** — seguradoras
- **LineOfBusiness** — ramos

### Seguros
- **Proposal** → **Policy** → **CoveredItem**
- **Claim** — sinistros
- **Endorsement** — endossos
- **Renewal** — renovações

### Comercial
- **Agent** / **Producer** — hierarquia comercial
- **Commission** / **CommissionSplit** — comissões e repasses

### CRM
- **Pipeline** → **Stage** → **Deal** → **DealStageHistory**

### IA
- **ChatSession** / **ChatMessage** — chat com IA

### Infra
- **Document** — anexos protegidos
- **Notification** — notificações in-app
