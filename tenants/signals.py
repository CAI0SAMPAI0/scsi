from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_plans(sender, **kwargs):
    """Create default subscription plans after migrations."""
    if sender.name != 'tenants':
        return
    from tenants.models import Plan
    plans = [
        {
            'name': 'Free',
            'slug': 'free',
            'price': '0.00',
            'max_users': 3,
            'max_clients': 100,
            'max_policies': 50,
            'features': {'basic_reports': True},
        },
        {
            'name': 'Starter',
            'slug': 'starter',
            'price': '97.00',
            'max_users': 10,
            'max_clients': 500,
            'max_policies': 250,
            'features': {'basic_reports': True, 'email_notifications': True},
        },
        {
            'name': 'Pro',
            'slug': 'pro',
            'price': '297.00',
            'max_users': None,
            'max_clients': None,
            'max_policies': None,
            'features': {
                'basic_reports': True,
                'advanced_reports': True,
                'email_notifications': True,
                'ai_agents': True,
                'api_access': True,
            },
        },
    ]
    for plan_data in plans:
        Plan.objects.get_or_create(
            slug=plan_data['slug'],
            defaults=plan_data,
        )
