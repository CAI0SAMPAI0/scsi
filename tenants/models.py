from decimal import Decimal
from django.db import models
from base.models import BaseModel


class Plan(models.Model):
    name          = models.CharField('nome', max_length=100)
    slug          = models.SlugField('slug', unique=True)
    price         = models.DecimalField('preço', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_available  = models.BooleanField('disponível', default=True)
    max_users     = models.PositiveIntegerField('máx. usuários', null=True, blank=True)
    max_clients   = models.PositiveIntegerField('máx. clientes', null=True, blank=True)
    max_policies  = models.PositiveIntegerField('máx. apólices', null=True, blank=True)
    features      = models.JSONField('funcionalidades', default=dict, blank=True)

    class Meta:
        verbose_name = 'plano'
        verbose_name_plural = 'planos'
        ordering = ('price',)

    def __str__(self):
        return self.name


class Brokerage(BaseModel):
    # Identification
    legal_name   = models.CharField('razão social', max_length=200)
    trade_name   = models.CharField('nome fantasia', max_length=200, blank=True)
    cnpj         = models.CharField('CNPJ', max_length=18, unique=True)
    susep_code   = models.CharField('código SUSEP', max_length=50, blank=True)
    # Contact
    email        = models.EmailField('e-mail')
    phone        = models.CharField('telefone', max_length=20, blank=True)
    # Address
    street       = models.CharField('logradouro', max_length=200, blank=True)
    number       = models.CharField('número', max_length=20, blank=True)
    complement   = models.CharField('complemento', max_length=100, blank=True)
    district     = models.CharField('bairro', max_length=100, blank=True)
    city         = models.CharField('cidade', max_length=100, blank=True)
    state        = models.CharField('estado', max_length=2, blank=True)
    zip_code     = models.CharField('CEP', max_length=9, blank=True)
    # Relations
    owner        = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='owned_brokerages',
        verbose_name='proprietário',
    )
    plan         = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='brokerages',
        verbose_name='plano',
    )
    is_active    = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'corretora'
        verbose_name_plural = 'corretoras'
        ordering = ('legal_name',)

    def __str__(self):
        return self.trade_name or self.legal_name


class Subscription(BaseModel):
    brokerage  = models.OneToOneField(
        Brokerage,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='corretora',
    )
    plan       = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        verbose_name='plano',
    )
    status     = models.CharField(
        'status',
        max_length=20,
        choices=[
            ('active',   'Ativo'),
            ('past_due', 'Inadimplente'),
            ('canceled', 'Cancelado'),
        ],
        default='active',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'assinatura'
        verbose_name_plural = 'assinaturas'

    def __str__(self):
        return f'{self.brokerage} – {self.get_status_display()}'
