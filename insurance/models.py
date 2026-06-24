from django.conf import settings
from django.db import models

from base.models import TenantAwareModel


class Proposal(TenantAwareModel):
    class Status(models.TextChoices):
        DRAFT         = 'draft',          'Rascunho'
        SENT          = 'sent',           'Enviada'
        UNDER_ANALYSIS = 'under_analysis', 'Em Análise'
        APPROVED      = 'approved',       'Aprovada'
        REJECTED      = 'rejected',       'Rejeitada'
        CONVERTED     = 'converted',      'Convertida'

    class SummaryStatus(models.TextChoices):
        IDLE       = 'idle',       'Aguardando'
        PROCESSING = 'processing', 'Processando'
        DONE       = 'done',       'Concluído'
        ERROR      = 'error',      'Erro'

    client = models.ForeignKey(
        'clients.Client', on_delete=models.PROTECT, related_name='proposals',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer', on_delete=models.PROTECT, related_name='proposals',
    )
    line_of_business = models.ForeignKey(
        'insurers.LineOfBusiness', on_delete=models.PROTECT, related_name='proposals',
    )
    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proposals_as_producer',
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proposals_as_agent',
    )
    number = models.CharField('número', max_length=30)
    status = models.CharField(
        'status', max_length=20,
        choices=Status.choices, default=Status.DRAFT,
    )
    net_premium = models.DecimalField('prêmio líquido', max_digits=12, decimal_places=2, default=0)
    total_premium = models.DecimalField('prêmio total', max_digits=12, decimal_places=2, default=0)
    iof = models.DecimalField('IOF', max_digits=12, decimal_places=2, default=0)
    proposed_start_date = models.DateField('início proposto', null=True, blank=True)
    proposed_end_date = models.DateField('fim proposto', null=True, blank=True)
    payment_terms = models.CharField('condições de pagamento', max_length=200, blank=True)
    notes = models.TextField('observações', blank=True)
    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status resumo IA', max_length=12,
        choices=SummaryStatus.choices, default=SummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField('resumo IA atualizado em', null=True, blank=True)

    class Meta:
        verbose_name = 'proposta'
        verbose_name_plural = 'propostas'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'number'],
                name='unique_proposal_number_per_brokerage',
            ),
        ]

    def __str__(self):
        return f'{self.number} — {self.client}'


class Policy(TenantAwareModel):
    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Ativa'
        CANCELED = 'canceled', 'Cancelada'
        EXPIRED  = 'expired',  'Expirada'
        RENEWED  = 'renewed',  'Renovada'

    class SummaryStatus(models.TextChoices):
        IDLE       = 'idle',       'Aguardando'
        PROCESSING = 'processing', 'Processando'
        DONE       = 'done',       'Concluído'
        ERROR      = 'error',      'Erro'

    proposal = models.ForeignKey(
        Proposal, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='policies',
    )
    policy_number = models.CharField('número da apólice', max_length=30)
    client = models.ForeignKey(
        'clients.Client', on_delete=models.PROTECT, related_name='policies',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer', on_delete=models.PROTECT, related_name='policies',
    )
    line_of_business = models.ForeignKey(
        'insurers.LineOfBusiness', on_delete=models.PROTECT, related_name='policies',
    )
    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='policies_as_producer',
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='policies_as_agent',
    )
    status = models.CharField(
        'status', max_length=20,
        choices=Status.choices, default=Status.ACTIVE,
    )
    net_premium = models.DecimalField('prêmio líquido', max_digits=12, decimal_places=2, default=0)
    total_premium = models.DecimalField('prêmio total', max_digits=12, decimal_places=2, default=0)
    iof = models.DecimalField('IOF', max_digits=12, decimal_places=2, default=0)
    commission_rate = models.DecimalField('taxa de comissão (%)', max_digits=5, decimal_places=2, default=0)
    start_date = models.DateField('início vigência', null=True, blank=True)
    end_date = models.DateField('fim vigência', null=True, blank=True)
    payment_info = models.CharField('dados de pagamento', max_length=200, blank=True)
    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status resumo IA', max_length=12,
        choices=SummaryStatus.choices, default=SummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField('resumo IA atualizado em', null=True, blank=True)

    class Meta:
        verbose_name = 'apólice'
        verbose_name_plural = 'apólices'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'policy_number'],
                name='unique_policy_number_per_brokerage',
            ),
        ]

    def __str__(self):
        return f'{self.policy_number} — {self.client}'


class CoveredItem(models.Model):
    class ItemType(models.TextChoices):
        AUTO      = 'auto',      'Auto'
        PROPERTY  = 'property',  'Residencial'
        FLEET     = 'fleet',     'Frota'
        TRAVEL    = 'travel',    'Viagem'
        LIFE      = 'life',      'Vida'
        EQUIPMENT = 'equipment', 'Equipamento'
        OTHER     = 'other',     'Outro'

    proposal = models.ForeignKey(
        Proposal, on_delete=models.CASCADE,
        null=True, blank=True, related_name='covered_items',
    )
    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE,
        null=True, blank=True, related_name='covered_items',
    )
    item_type = models.CharField('tipo', max_length=20, choices=ItemType.choices)
    description = models.CharField('descrição', max_length=300)
    identifier = models.CharField('identificador (placa/chassi/endereço)', max_length=100, blank=True)
    insured_amount = models.DecimalField('valor segurado', max_digits=14, decimal_places=2, default=0)
    attributes = models.JSONField('atributos', default=dict, blank=True)
    coverages = models.JSONField('coberturas', default=dict, blank=True)

    class Meta:
        verbose_name = 'item segurado'
        verbose_name_plural = 'itens segurados'
        ordering = ('id',)
        constraints = [
            models.CheckConstraint(
                name='covered_item_exactly_one_parent',
                condition=(
                    (models.Q(proposal__isnull=False) & models.Q(policy__isnull=True))
                    | (models.Q(proposal__isnull=True) & models.Q(policy__isnull=False))
                ),
            ),
        ]

    def __str__(self):
        return f'{self.get_item_type_display()} — {self.description}'
