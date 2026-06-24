from django.db import models
from base.managers import TenantManager


class BaseModel(models.Model):
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class TenantAwareModel(BaseModel):
    brokerage = models.ForeignKey(
        'tenants.Brokerage',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        db_index=True,
    )
    objects = TenantManager()

    class Meta:
        abstract = True
        indexes = [models.Index(fields=['brokerage'])]
