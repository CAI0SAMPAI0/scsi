from celery import shared_task


def _get_owner(brokerage):
    from accounts.models import User
    return User.objects.filter(brokerage=brokerage, role='owner', is_active=True).first()


@shared_task
def generate_client_summary(client_id):
    from clients.models import Client
    from ai_agents.summary import summarize_entity
    from notifications.views import create_notification

    client = Client.objects.select_related('brokerage').get(pk=client_id)

    def fetch_data(c):
        return {
            'name': c.name, 'document': c.document, 'email': c.email,
            'phone': c.phone, 'person_type': c.person_type,
            'policies_count': c.policies.count(),
            'proposals_count': c.proposals.count(),
            'claims_count': c.claims.count(),
        }

    summarize_entity(client, 'Cliente', fetch_data)

    owner = _get_owner(client.brokerage)
    if owner:
        create_notification(
            user=owner, brokerage=client.brokerage,
            type='ai_summary',
            title=f'Resumo do cliente {client.name} pronto',
            message='O resumo do cliente foi gerado com sucesso.',
            url=f'/clientes/{client.pk}/',
        )


@shared_task
def generate_policy_summary(policy_id):
    from insurance.models import Policy
    from ai_agents.summary import summarize_entity
    from notifications.views import create_notification

    policy = Policy.objects.select_related('brokerage', 'client', 'insurer').get(pk=policy_id)

    def fetch_data(p):
        return {
            'policy_number': p.policy_number, 'client': p.client.name,
            'insurer': p.insurer.name, 'status': p.status,
            'total_premium': str(p.total_premium),
            'start_date': str(p.start_date), 'end_date': str(p.end_date),
            'items_count': p.covered_items.count(),
            'claims_count': p.claims.count(),
            'endorsements_count': p.endorsements.count(),
        }

    summarize_entity(policy, 'Apólice', fetch_data)

    owner = _get_owner(policy.brokerage)
    if owner:
        create_notification(
            user=owner, brokerage=policy.brokerage,
            type='ai_summary',
            title=f'Resumo da apólice {policy.policy_number} pronto',
            message='O resumo da apólice foi gerado com sucesso.',
            url=f'/apolices/{policy.pk}/',
        )


@shared_task
def generate_claim_summary(claim_id):
    from claims.models import Claim
    from ai_agents.summary import summarize_entity
    from notifications.views import create_notification

    claim = Claim.objects.select_related('brokerage', 'policy', 'covered_item').get(pk=claim_id)

    def fetch_data(c):
        return {
            'claim_number': c.claim_number,
            'policy_number': c.policy.policy_number,
            'status': c.status,
            'claimed_amount': str(c.claimed_amount),
            'approved_amount': str(c.approved_amount or 0),
            'occurrence_date': str(c.occurrence_date),
            'notice_date': str(c.notice_date),
            'description': c.description,
        }

    summarize_entity(claim, 'Sinistro', fetch_data)

    owner = _get_owner(claim.brokerage)
    if owner:
        create_notification(
            user=owner, brokerage=claim.brokerage,
            type='ai_summary',
            title=f'Resumo do sinistro {claim.claim_number} pronto',
            message='O resumo do sinistro foi gerado com sucesso.',
            url=f'/sinistros/{claim.pk}/',
        )


@shared_task
def generate_proposal_summary(proposal_id):
    from insurance.models import Proposal
    from ai_agents.summary import summarize_entity
    from notifications.views import create_notification

    proposal = Proposal.objects.select_related('brokerage', 'client', 'insurer').get(pk=proposal_id)

    def fetch_data(p):
        return {
            'number': p.number, 'client': p.client.name,
            'insurer': p.insurer.name, 'status': p.status,
            'total_premium': str(p.total_premium),
            'items_count': p.covered_items.count(),
        }

    summarize_entity(proposal, 'Proposta', fetch_data)

    owner = _get_owner(proposal.brokerage)
    if owner:
        create_notification(
            user=owner, brokerage=proposal.brokerage,
            type='ai_summary',
            title=f'Resumo da proposta {proposal.number} pronto',
            message='O resumo da proposta foi gerado com sucesso.',
            url=f'/propostas/{proposal.pk}/',
        )


@shared_task
def generate_deal_summary(deal_id):
    from crm.models import Deal
    from ai_agents.summary import summarize_entity
    from notifications.views import create_notification

    deal = Deal.objects.select_related('brokerage', 'client', 'stage').get(pk=deal_id)

    def fetch_data(d):
        return {
            'title': d.title, 'status': d.status,
            'client': d.client.name if d.client else 'N/A',
            'stage': d.stage.name if d.stage else 'N/A',
            'estimated_value': str(d.estimated_value),
            'description': d.description,
        }

    summarize_entity(deal, 'Negociação', fetch_data)

    owner = _get_owner(deal.brokerage)
    if owner:
        create_notification(
            user=owner, brokerage=deal.brokerage,
            type='ai_summary',
            title=f'Resumo da negociação {deal.title} pronto',
            message='O resumo da negociação foi gerado com sucesso.',
            url=f'/crm/negociacoes/{deal.pk}/',
        )
