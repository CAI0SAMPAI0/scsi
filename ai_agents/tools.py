from django.db.models import Q


def build_tenant_tools(brokerage):
    """Build tenant-scoped tools for AI agents."""

    def list_clients(query=''):
        from clients.models import Client
        qs = Client.objects.filter(brokerage=brokerage, is_active=True)
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(document__icontains=query))
        results = []
        for c in qs[:20]:
            results.append({
                'id': c.pk,
                'name': c.name,
                'document': c.document,
                'person_type': c.person_type,
                'email': c.email,
                'phone': c.phone,
            })
        return results

    def get_client(name=''):
        from clients.models import Client
        c = Client.objects.filter(
            Q(brokerage=brokerage) & (Q(name__icontains=name) | Q(document__icontains=name)),
        ).first()
        if not c:
            return {'error': 'Cliente não encontrado'}
        policies = list(c.policies.values('policy_number', 'status', 'total_premium'))
        proposals = list(c.proposals.values('number', 'status', 'total_premium'))
        return {
            'id': c.pk, 'name': c.name, 'document': c.document,
            'email': c.email, 'phone': c.phone,
            'policies': policies, 'proposals': proposals,
            'ai_summary': c.ai_summary or '',
        }

    def list_policies(status=''):
        from insurance.models import Policy
        qs = Policy.objects.filter(brokerage=brokerage)
        if status:
            qs = qs.filter(status=status)
        results = []
        for p in qs[:20]:
            results.append({
                'id': p.pk,
                'policy_number': p.policy_number,
                'client': p.client.name,
                'status': p.status,
                'total_premium': str(p.total_premium),
                'start_date': str(p.start_date),
                'end_date': str(p.end_date),
            })
        return results

    def get_policy(policy_number=''):
        from insurance.models import Policy
        p = Policy.objects.filter(
            brokerage=brokerage, policy_number__icontains=policy_number,
        ).first()
        if not p:
            return {'error': 'Apólice não encontrada'}
        items = list(p.covered_items.values('item_type', 'description', 'insured_amount'))
        return {
            'id': p.pk, 'policy_number': p.policy_number,
            'client': p.client.name, 'insurer': p.insurer.name,
            'status': p.status, 'total_premium': str(p.total_premium),
            'start_date': str(p.start_date), 'end_date': str(p.end_date),
            'items': items, 'ai_summary': p.ai_summary or '',
        }

    def list_claims(status=''):
        from claims.models import Claim
        qs = Claim.objects.filter(brokerage=brokerage)
        if status:
            qs = qs.filter(status=status)
        results = []
        for c in qs[:20]:
            results.append({
                'id': c.pk, 'claim_number': c.claim_number,
                'policy': c.policy.policy_number,
                'status': c.status, 'claimed_amount': str(c.claimed_amount),
                'occurrence_date': str(c.occurrence_date),
            })
        return results

    def list_renewals_due():
        from insurance.models import Renewal
        from datetime import date, timedelta
        threshold = date.today() + timedelta(days=90)
        renewals = Renewal.objects.filter(
            brokerage=brokerage,
            status='pending',
            due_date__lte=threshold,
        ).select_related('policy', 'policy__client')[:20]
        results = []
        for r in renewals:
            results.append({
                'id': r.pk,
                'policy_number': r.policy.policy_number,
                'client': r.policy.client.name,
                'due_date': str(r.due_date),
                'status': r.status,
            })
        return results

    def commissions_summary():
        from commissions.models import Commission
        from django.db.models import Sum
        qs = Commission.objects.filter(brokerage=brokerage)
        total = qs.aggregate(total=Sum('insurer_amount'))['total'] or 0
        pending = qs.filter(status='pending').aggregate(total=Sum('insurer_amount'))['total'] or 0
        received = qs.filter(status='received').aggregate(total=Sum('insurer_amount'))['total'] or 0
        return {
            'total_commission': str(total),
            'pending': str(pending),
            'received': str(received),
        }

    return {
        'list_clients': list_clients,
        'get_client': get_client,
        'list_policies': list_policies,
        'get_policy': get_policy,
        'list_claims': list_claims,
        'list_renewals_due': list_renewals_due,
        'commissions_summary': commissions_summary,
    }
