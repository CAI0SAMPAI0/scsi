from django.db import transaction


def generate_policy_from_proposal(proposal, policy_number, brokerage, commission_rate=0):
    """Atomically generate a Policy from a Proposal."""
    from insurance.models import Policy, CoveredItem

    if proposal.status == 'converted':
        raise ValueError('Proposta já foi convertida em apólice.')

    with transaction.atomic():
        policy = Policy.objects.create(
            brokerage=brokerage,
            proposal=proposal,
            policy_number=policy_number,
            client=proposal.client,
            insurer=proposal.insurer,
            line_of_business=proposal.line_of_business,
            producer=proposal.producer,
            agent=proposal.agent,
            status='active',
            net_premium=proposal.net_premium,
            total_premium=proposal.total_premium,
            iof=proposal.iof,
            commission_rate=commission_rate,
            start_date=proposal.proposed_start_date,
            end_date=proposal.proposed_end_date,
        )

        for item in CoveredItem.objects.filter(proposal=proposal):
            item.pk = None
            item.proposal = None
            item.policy = policy
            item.save()

        proposal.status = 'converted'
        proposal.save(update_fields=['status'])

        from commissions.services import calculate_commission
        calculate_commission(policy)

    return policy
