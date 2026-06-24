from django.db import models
from django.core.validators import MinLengthValidator
from base.models import TenantAwareModel


class Client(TenantAwareModel):
    class PersonType(models.TextChoices):
        PF = 'PF', 'Pessoa Física'
        PJ = 'PJ', 'Pessoa Jurídica'

    class SummaryStatus(models.TextChoices):
        IDLE       = 'idle',       'Aguardando'
        PROCESSING = 'processing', 'Processando'
        DONE       = 'done',      'Concluído'
        ERROR      = 'error',     'Erro'

    person_type = models.CharField(
        'tipo de pessoa',
        max_length=2,
        choices=PersonType.choices,
        default=PersonType.PF,
    )
    name = models.CharField('nome / razão social', max_length=200)
    trade_name = models.CharField('nome fantasia', max_length=200, blank=True)
    document = models.CharField(
        'CPF / CNPJ',
        max_length=18,
        validators=[MinLengthValidator(11)],
    )
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=20, blank=True)
    birth_date = models.DateField('data de nascimento', null=True, blank=True)
    street = models.CharField('logradouro', max_length=200, blank=True)
    number = models.CharField('número', max_length=20, blank=True)
    complement = models.CharField('complemento', max_length=100, blank=True)
    district = models.CharField('bairro', max_length=100, blank=True)
    city = models.CharField('cidade', max_length=100, blank=True)
    state = models.CharField('estado', max_length=2, blank=True)
    zip_code = models.CharField('CEP', max_length=9, blank=True)
    notes = models.TextField('observações', blank=True)
    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status resumo IA',
        max_length=12,
        choices=SummaryStatus.choices,
        default=SummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField('resumo IA atualizado em', null=True, blank=True)
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'document'],
                name='%(class)s brokerage document unique',
            ),
        ]
        indexes = [
            models.Index(fields=['brokerage', 'name']),
        ]

    def __str__(self):
        return self.name

    @property
    def document_display(self):
        doc = self.document
        if self.person_type == self.PersonType.PF and len(doc) == 11:
            return f'{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}'
        if self.person_type == self.PersonType.PJ and len(doc) == 14:
            return f'{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}'
        return doc
