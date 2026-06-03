from django.contrib.auth.models import User
from .models import Notification


def notify_admins(notif_type, title, body='', link=''):
    """Crée une notification pour tous les staff/superusers."""
    admins = User.objects.filter(is_staff=True)
    notifications = [
        Notification(
            recipient=admin,
            notif_type=notif_type,
            title=title,
            body=body,
            link=link,
        )
        for admin in admins
    ]
    Notification.objects.bulk_create(notifications)
