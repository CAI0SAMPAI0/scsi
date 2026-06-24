import os
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from base.models import TenantAwareModel


def document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'brokerage_{instance.brokerage_id}/{uuid.uuid4().hex}{ext}'


class Document(TenantAwareModel):
    uploaded_by    = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='enviado por',
    )
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    file              = models.FileField(upload_to=document_upload_path, verbose_name='arquivo')
    original_filename = models.CharField('nome original', max_length=255)
    mime_type         = models.CharField('tipo MIME', max_length=100)
    size              = models.PositiveIntegerField('tamanho (bytes)')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'

    def __str__(self):
        return self.original_filename

    @property
    def size_display(self):
        if self.size < 1024:
            return f'{self.size} B'
        elif self.size < 1024 * 1024:
            return f'{self.size / 1024:.1f} KB'
        return f'{self.size / (1024 * 1024):.1f} MB'
