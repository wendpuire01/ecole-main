from django.db import models
from django.contrib.auth.models import User


class Anonce(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now=True)
    update_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    TYPE_CHOICES = [
        ('payment',    'Paiement'),
        ('enrollment', 'Inscription'),
        ('overdue',    'Retard de paiement'),
    ]

    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type  = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title       = models.CharField(max_length=200)
    body        = models.TextField(blank=True)
    link        = models.CharField(max_length=300, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.title}"

