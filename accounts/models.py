from django.contrib.auth.models import AbstractUser
from django.db import models
from base.models import BaseModel
from accounts.managers import UserManager


class User(AbstractUser, BaseModel):
    class Role(models.TextChoices):
        OWNER       = 'owner',       'Administrador'
        MANAGER     = 'manager',     'Gerente'
        BROKER      = 'broker',      'Corretor'
        AGENT       = 'agent',       'Agente'
        PRODUCER    = 'producer',    'Produtor'
        OPERATIONAL = 'operational', 'Operacional'

    username = None
    email = models.EmailField('e-mail', unique=True)
    brokerage = models.ForeignKey(
        'tenants.Brokerage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='corretora',
    )
    role = models.CharField(
        'perfil',
        max_length=20,
        choices=Role.choices,
        default=Role.OPERATIONAL,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    @property
    def role_display(self):
        return self.get_role_display()

    @property
    def initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[-1][0]}'.upper()
        return self.email[:2].upper()
