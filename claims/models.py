from django.db import models

from base.models import TenantAwareModel


class Claim(TenantAwareModel):
    class Status(models.TextChoices):
        OPENED = 'opened', 'Aberto'
        UNDER_ANALYSIS = 'under_analysis', 'Em análise'
        APPROVED = 'approved', 'Aprovado'
        DENIED = 'denied', 'Negado'
        PAID = 'paid', 'Pago'
        CLOSED = 'closed', 'Fechado'

    class AiSummaryStatus(models.TextChoices):
        IDLE = 'idle', 'Ocioso'
        PROCESSING = 'processing', 'Processando'
        DONE = 'done', 'Concluído'
        ERROR = 'error', 'Erro'

    policy = models.ForeignKey(
        'insurance.Policy',
        on_delete=models.PROTECT,
        related_name='claims',
    )
    covered_item = models.ForeignKey(
        'insurance.CoveredItem',
        on_delete=models.PROTECT,
        related_name='claims',
    )
    claim_number = models.CharField('número do sinistro', max_length=30)
    occurrence_date = models.DateField('data da ocorrência')
    notice_date = models.DateField('data do aviso', null=True, blank=True)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.OPENED,
    )
    description = models.TextField('descrição', blank=True)
    claimed_amount = models.DecimalField(
        'valor reclamado', max_digits=14, decimal_places=2, default=0,
    )
    approved_amount = models.DecimalField(
        'valor aprovado', max_digits=14, decimal_places=2, default=0,
    )
    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status do resumo IA',
        max_length=12,
        choices=AiSummaryStatus.choices,
        default=AiSummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField(
        'resumo IA atualizado em', null=True, blank=True,
    )

    class Meta(TenantAwareModel.Meta):
        ordering = ('-created_at',)
        verbose_name = 'sinistro'
        verbose_name_plural = 'sinistros'

    def __str__(self):
        return self.claim_number


class Endorsement(TenantAwareModel):
    class Type(models.TextChoices):
        INCREASE = 'increase', 'Acréscimo'
        DECREASE = 'decrease', 'Redução'
        CANCELLATION = 'cancellation', 'Cancelamento'
        DATA_CHANGE = 'data_change', 'Alteração de dados'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        APPLIED = 'applied', 'Aplicado'
        CANCELED = 'canceled', 'Cancelado'

    policy = models.ForeignKey(
        'insurance.Policy',
        on_delete=models.PROTECT,
        related_name='endorsements',
    )
    endorsement_number = models.CharField('número do endosso', max_length=30)
    type = models.CharField('tipo', max_length=20, choices=Type.choices)
    description = models.TextField('descrição', blank=True)
    premium_change = models.DecimalField(
        'variação do prêmio', max_digits=12, decimal_places=2, default=0,
    )
    effective_date = models.DateField('data de vigência', null=True, blank=True)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta(TenantAwareModel.Meta):
        ordering = ('-created_at',)
        verbose_name = 'endosso'
        verbose_name_plural = 'endossos'

    def __str__(self):
        return self.endorsement_number
