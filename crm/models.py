from django.conf import settings
from django.db import models
from base.models import TenantAwareModel


class Pipeline(TenantAwareModel):
    name = models.CharField('nome', max_length=100)
    is_default = models.BooleanField('padrão', default=False)

    class Meta:
        verbose_name = 'pipeline'
        verbose_name_plural = 'pipelines'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Stage(TenantAwareModel):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name='pipeline',
    )
    name = models.CharField('nome', max_length=100)
    color = models.CharField('cor', max_length=7, default='#3454d1')
    order = models.PositiveIntegerField('ordem', default=0)
    is_won = models.BooleanField('etapa de ganho', default=False)
    is_lost = models.BooleanField('etapa de perda', default=False)

    class Meta:
        verbose_name = 'etapa'
        verbose_name_plural = 'etapas'
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(fields=['pipeline', 'order'], name='unique_stage_order_per_pipeline'),
        ]

    def __str__(self):
        return f'{self.pipeline.name} - {self.name}'


class Deal(TenantAwareModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Aberto'
        WON  = 'won',  'Ganho'
        LOST = 'lost', 'Perdido'

    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name='pipeline',
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deals',
        verbose_name='etapa',
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deals',
        verbose_name='cliente',
    )
    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deals_as_producer',
        verbose_name='produtor',
    )
    agent = models.ForeignKey(
        'partners.Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deals',
        verbose_name='agente',
    )
    line_of_business = models.ForeignKey(
        'insurers.LineOfBusiness',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deals',
        verbose_name='ramo',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deals',
        verbose_name='seguradora',
    )
    proposal = models.ForeignKey(
        'insurance.Proposal',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deals',
        verbose_name='proposta',
    )
    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição', blank=True)
    estimated_value = models.DecimalField(
        'valor estimado', max_digits=14, decimal_places=2, default=0,
    )
    status = models.CharField('status', max_length=10, choices=Status.choices, default=Status.OPEN)
    expected_close_date = models.DateField('previsão de fechamento', null=True, blank=True)
    ai_summary = models.TextField('resumo IA', blank=True)
    ai_summary_status = models.CharField('status resumo IA', max_length=15, default='idle')

    class Meta:
        verbose_name = 'negociação'
        verbose_name_plural = 'negociações'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['brokerage', 'status']),
            models.Index(fields=['brokerage', 'stage']),
        ]

    def __str__(self):
        return self.title


class DealStageHistory(TenantAwareModel):
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='stage_history',
        verbose_name='negociação',
    )
    from_stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='history_from',
        verbose_name='etapa origem',
    )
    to_stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='history_to',
        verbose_name='etapa destino',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deal_stage_changes',
        verbose_name='alterado por',
    )
    changed_at = models.DateTimeField('alterado em', auto_now_add=True)
    note = models.TextField('observação', blank=True)

    class Meta:
        verbose_name = 'histórico de etapa'
        verbose_name_plural = 'históricos de etapa'
        ordering = ('-changed_at',)

    def __str__(self):
        return f'{self.deal} | {self.from_stage} → {self.to_stage}'
