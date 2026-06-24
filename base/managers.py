from contextvars import ContextVar
from django.db import models

current_tenant = ContextVar('current_tenant', default=None)


class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(brokerage=tenant)


class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)
