from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from notifications.models import Notification


class NotificationUnreadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        if not tenant:
            return JsonResponse({'count': 0, 'notifications': []})

        unread = Notification.objects.filter(
            brokerage=tenant,
            user=request.user,
            is_read=False,
        ).order_by('-created_at')[:20]

        data = {
            'count': Notification.objects.filter(
                brokerage=tenant, user=request.user, is_read=False
            ).count(),
            'notifications': [
                {
                    'id': n.pk,
                    'title': n.title,
                    'message': n.message,
                    'url': n.url,
                    'type': n.type,
                    'created_at': n.created_at.strftime('%d/%m/%H:%M'),
                }
                for n in unread
            ],
        }
        return JsonResponse(data)


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        if not tenant:
            return JsonResponse({'ok': True})

        notification_id = kwargs.get('pk')
        if notification_id:
            Notification.objects.filter(
                pk=notification_id, brokerage=tenant, user=request.user
            ).update(is_read=True, read_at=timezone.now())
        else:
            Notification.objects.filter(
                brokerage=tenant, user=request.user, is_read=False
            ).update(is_read=True, read_at=timezone.now())

        return JsonResponse({'ok': True})


def create_notification(user, brokerage, type, title, message, url=''):
    """Helper to create a notification."""
    return Notification.objects.create(
        brokerage=brokerage,
        user=user,
        type=type,
        title=title,
        message=message,
        url=url,
    )
