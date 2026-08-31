from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin',     'Administrateur'),
        ('founder',   'Fondateur'),
        ('director',  'Directeur'),
        ('educator',  'Surveillant'),   # gère académique + inscriptions, pas paiements
        ('teacher',   'Enseignant'),    # saisit les notes de ses classes uniquement
        ('cashier',   'Caissier'),      # gère paiements + inscriptions
    ]

    SUPER_ROLES          = ('admin', 'founder')
    ACADEMIC_ROLES       = ('admin', 'founder', 'director', 'educator', 'teacher')
    PAYMENT_ROLES        = ('admin', 'founder', 'director', 'cashier')
    ENROLLMENT_ROLES     = ('admin', 'founder', 'director', 'educator', 'cashier')
    TEACHER_MGMT_ROLES   = ('admin', 'founder', 'director', 'educator')
    MGMT_ROLES           = ('admin', 'founder', 'director')

    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    teacher   = models.ForeignKey(
        'school_portal.Teacher', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='user_account',
        verbose_name='Enseignant lié'
    )
    phone     = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    # ── Helpers ──
    @property
    def is_admin(self):
        return self.role in self.SUPER_ROLES

    @property
    def is_director(self):
        return self.role in ('admin', 'founder', 'director')

    @property
    def can_manage_academic(self):
        return self.role in self.ACADEMIC_ROLES

    @property
    def can_manage_payments(self):
        return self.role in self.PAYMENT_ROLES

    @property
    def can_manage_enrollments(self):
        return self.role in self.ENROLLMENT_ROLES

    @property
    def can_manage_finance(self):
        return self.can_manage_payments or self.can_manage_enrollments

    @property
    def can_manage_teachers(self):
        return self.role in self.TEACHER_MGMT_ROLES

    @property
    def can_manage_settings(self):
        return self.role in self.MGMT_ROLES

    @property
    def can_manage_users(self):
        return self.role in self.SUPER_ROLES


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


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

