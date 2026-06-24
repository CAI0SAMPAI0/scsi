from django.db.models.signals import post_migrate, post_save
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


@receiver(post_save, sender='tenants.Brokerage')
def create_default_pipeline(sender, instance, created, **kwargs):
    if not created:
        return
    from crm.models import Pipeline, Stage
    pipeline = Pipeline.objects.create(
        brokerage=instance,
        name='Vendas',
        is_default=True,
    )
    stages = [
        ('Novo Lead', '#3454d1', 0),
        ('Em Cotação', '#f5a623', 1),
        ('Proposta', '#9b59b6', 2),
        ('Ganho', '#17c666', 3),
        ('Perdido', '#ea4d4d', 4),
    ]
    for name, color, order in stages:
        is_won = name == 'Ganho'
        is_lost = name == 'Perdido'
        Stage.objects.create(
            brokerage=instance,
            pipeline=pipeline,
            name=name,
            color=color,
            order=order,
            is_won=is_won,
            is_lost=is_lost,
        )
