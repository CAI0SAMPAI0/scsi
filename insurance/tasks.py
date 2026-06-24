from datetime import timedelta
from celery import shared_task
from django.utils import timezone


@shared_task
def check_renewals_due():
    """Create/update Renewals for policies expiring within 90 days."""
    from insurance.models import Policy, Renewal
    from notifications.views import create_notification
    from accounts.models import User

    today = timezone.now().date()
    threshold = today + timedelta(days=90)

    policies = Policy.objects.filter(
        status='active',
        end_date__lte=threshold,
        end_date__gte=today,
    )

    for policy in policies:
        renewal, created = Renewal.objects.get_or_create(
            brokerage=policy.brokerage,
            policy=policy,
            defaults={
                'status': Renewal.Status.PENDING,
                'due_date': policy.end_date,
            },
        )

        if created or renewal.status == Renewal.Status.PENDING:
            days_until = (policy.end_date - today).days
            if days_until <= 30:
                owner = User.objects.filter(
                    brokerage=policy.brokerage, role='owner', is_active=True
                ).first()
                if owner:
                    create_notification(
                        user=owner,
                        brokerage=policy.brokerage,
                        type='renewal',
                        title=f'Apólice {policy.policy_number} vence em {days_until} dias',
                        message=f'A apólice {policy.policy_number} do cliente {policy.client.name} vence em {days_until} dias.',
                        url=f'/apolices/{policy.pk}/',
                    )


@shared_task
def expire_policies():
    """Mark policies as expired if end_date has passed."""
    from insurance.models import Policy

    today = timezone.now().date()
    Policy.objects.filter(
        status='active',
        end_date__lt=today,
    ).update(status='expired')
