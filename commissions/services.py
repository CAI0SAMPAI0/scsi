from decimal import Decimal
from django.db.models import Sum
from commissions.models import Commission, CommissionSplit


def calculate_commission(policy):
    """Generate Commission + CommissionSplit for a policy."""
    if not policy.commission_rate or policy.commission_rate == 0:
        return None

    insurer_amount = (policy.total_premium * policy.commission_rate / Decimal('100')).quantize(
        Decimal('0.01')
    )

    commission = Commission.objects.create(
        brokerage=policy.brokerage,
        policy=policy,
        base_premium=policy.total_premium,
        insurer_rate=policy.commission_rate,
        insurer_amount=insurer_amount,
        status=Commission.Status.PENDING,
        reference_date=policy.start_date,
    )

    agent = getattr(policy, 'agent', None)
    producer = getattr(policy, 'producer', None)

    if agent and agent.default_commission_rate > 0:
        rate = agent.default_commission_rate
        amount = (insurer_amount * rate / Decimal('100')).quantize(Decimal('0.01'))
        if amount <= insurer_amount:
            CommissionSplit.objects.create(
                brokerage=policy.brokerage,
                commission=commission,
                beneficiary_type=CommissionSplit.BeneficiaryType.AGENT,
                agent=agent,
                rate=rate,
                amount=amount,
                status=CommissionSplit.Status.PENDING,
            )

    if producer and producer.default_commission_rate > 0:
        rate = producer.default_commission_rate
        amount = (insurer_amount * rate / Decimal('100')).quantize(Decimal('0.01'))
        existing = commission.splits.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        if amount + existing <= insurer_amount:
            CommissionSplit.objects.create(
                brokerage=policy.brokerage,
                commission=commission,
                beneficiary_type=CommissionSplit.BeneficiaryType.PRODUCER,
                producer=producer,
                rate=rate,
                amount=amount,
                status=CommissionSplit.Status.PENDING,
            )

    return commission
