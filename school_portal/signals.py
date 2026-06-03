from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment


@receiver(post_save, sender=Enrollment)
def notify_new_enrollment(sender, instance, created, **kwargs):
    if not created:
        return
    from main.notifications import notify_admins
    student = instance.student
    nom = f"{student.name} {student.first_name}"
    classe = instance.classe.name if instance.classe else ''
    type_label = instance.get_enrollment_type_display() if hasattr(instance, 'get_enrollment_type_display') else ''

    title = f"Nouvelle inscription — {nom}"
    body = f"{nom} inscrit(e) en {classe} ({type_label})" if classe else f"{nom} inscrit(e)"
    notify_admins('enrollment', title, body, link='')
