from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='tenants.Brokerage')
def create_default_lines_of_business(sender, instance, created, **kwargs):
    if not created:
        return
    from insurers.models import LineOfBusiness
    defaults = [
        ('Auto', 'auto'),
        ('Vida', 'life'),
        ('Residencial', 'property'),
        ('Empresarial', 'business'),
        ('Viagem', 'travel'),
        ('Saúde', 'health'),
        ('Responsabilidade Civil', 'other'),
        ('Frota', 'auto'),
        ('Equipamentos', 'business'),
        ('Condomínio', 'property'),
        ('Agronegócio', 'business'),
        ('Transporte', 'other'),
        ('Outros', 'other'),
    ]
    for name, category in defaults:
        LineOfBusiness.objects.get_or_create(
            brokerage=instance,
            name=name,
            defaults={'category': category},
        )
