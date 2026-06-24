from django.db import models
from base.models import TenantAwareModel


class Commission(TenantAwareModel):
    policy = models.ForeignKey(
        'insurance.Policy',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name='apólice',
    )
    base_premium = models.DecimalField('prêmio base', max_digits=14, decimal_places=2)
    insurer_rate = models.DecimalField('taxa seguradora (%)', max_digits=6, decimal_places=4)
    insurer_amount = models.DecimalField('valor recebido', max_digits=14, decimal_places=2)

    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pendente'
        RECEIVED = 'received', 'Recebida'
        PAID     = 'paid',     'Paga'

    status = models.CharField('status', max_length=10, choices=Status.choices, default=Status.PENDING)
    reference_date = models.DateField('data de referência')

    class Meta:
        verbose_name = 'comissão'
        verbose_name_plural = 'comissões'
        ordering = ('-reference_date',)
        indexes = [
            models.Index(fields=['brokerage', 'status']),
            models.Index(fields=['brokerage', 'reference_date']),
        ]

    def __str__(self):
        return f'Comissão #{self.pk} - {self.policy}'


class CommissionSplit(TenantAwareModel):
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name='splits',
        verbose_name='comissão',
    )

    class BeneficiaryType(models.TextChoices):
        AGENT   = 'agent',   'Agente'
        PRODUCER = 'producer', 'Produtor'

    beneficiary_type = models.CharField('tipo beneficiário', max_length=10, choices=BeneficiaryType.choices)
    agent = models.ForeignKey(
        'partners.Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='commission_splits',
        verbose_name='agente',
    )
    producer = models.ForeignKey(
        'partners.Producer',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='commission_splits',
        verbose_name='produtor',
    )
    rate = models.DecimalField('taxa repasse (%)', max_digits=6, decimal_places=4)
    amount = models.DecimalField('valor repasse', max_digits=14, decimal_places=2)

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PAID    = 'paid',    'Pago'

    status = models.CharField('status', max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField('pago em', null=True, blank=True)

    class Meta:
        verbose_name = 'repasse'
        verbose_name_plural = 'repasses'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['brokerage', 'status']),
        ]

    def __str__(self):
        return f'Repasse {self.get_beneficiary_type_display()} - {self.amount}'
