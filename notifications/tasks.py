from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_async_email(self, subject, message, recipient_list, from_email=None):
    """Send email asynchronously via Celery."""
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
