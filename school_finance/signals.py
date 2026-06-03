from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import Payment


@receiver(post_save, sender=Payment)
def notify_new_payment(sender, instance, created, **kwargs):
    if not created:
        return
    from main.notifications import notify_admins
    student = instance.student
    nom = f"{student.name} {student.first_name}"
    montant = f"{instance.paid_amount:,.0f} FCFA"
    fee = instance.fee_type.name if instance.fee_type else ''

    title = f"Nouveau paiement — {nom}"
    body = f"{nom} a versé {montant} ({fee})"
    try:
        link = reverse('payment_detail', args=[instance.pk])
    except Exception:
        link = ''

    notify_admins('payment', title, body, link)
