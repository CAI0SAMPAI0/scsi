from django.db import models
from base.models import TenantAwareModel


class Insurer(TenantAwareModel):
    name        = models.CharField('nome', max_length=200)
    cnpj        = models.CharField('CNPJ', max_length=18, blank=True)
    susep_code  = models.CharField('código SUSEP', max_length=50, blank=True)
    email       = models.EmailField('e-mail', blank=True)
    phone       = models.CharField('telefone', max_length=20, blank=True)
    is_active   = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'seguradora'
        verbose_name_plural = 'seguradoras'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['brokerage', 'name'], name='unique_insurer_per_brokerage'),
        ]

    def __str__(self):
        return self.name


class LineOfBusiness(TenantAwareModel):
    class Category(models.TextChoices):
        AUTO        = 'auto', 'Auto'
        LIFE        = 'life', 'Vida'
        PROPERTY    = 'property', 'Residencial'
        BUSINESS    = 'business', 'Empresarial'
        TRAVEL      = 'travel', 'Viagem'
        HEALTH      = 'health', 'Saúde'
        OTHER       = 'other', 'Outros'

    name     = models.CharField('nome', max_length=100)
    code     = models.CharField('código SUSEP', max_length=20, blank=True)
    category = models.CharField('categoria', max_length=20, choices=Category.choices)
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'ramo'
        verbose_name_plural = 'ramos'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['brokerage', 'name'], name='unique_lob_per_brokerage'),
        ]

    def __str__(self):
        return self.name
