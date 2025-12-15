from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from school_portal.models import Student, Class


class AcademicYear(models.Model):
    """Année scolaire"""
    name = models.CharField(max_length=20, unique=True, verbose_name="Année")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    is_active = models.BooleanField(default=False, verbose_name="Année active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Année Scolaire"
        verbose_name_plural = "Années Scolaires"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # Désactiver toutes les autres années
            AcademicYear.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class FeeType(models.Model):
    """Types de frais"""
    CATEGORY_CHOICES = [
        ('inscription', 'Inscription'),
        ('reinscription', 'Réinscription'),
        ('scolarite', 'Scolarité'),
        ('examen', 'Frais d\'examen'),
        ('cantine', 'Cantine'),
        ('transport', 'Transport'),
        ('uniforme', 'Uniforme'),
        ('materiel', 'Matériel scolaire'),
        ('activite', 'Activités'),
        ('autre', 'Autres frais'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom du frais")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    is_mandatory = models.BooleanField(default=True, verbose_name="Obligatoire")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Type de Frais"
        verbose_name_plural = "Types de Frais"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class FeeStructure(models.Model):
    """Structure des frais par classe"""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Année scolaire")
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="Classe")
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, verbose_name="Type de frais")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant (FCFA)"
    )
    payment_frequency = models.CharField(
        max_length=20,
        choices=[
            ('unique', 'Paiement unique'),
            ('mensuel', 'Mensuel'),
            ('trimestriel', 'Trimestriel'),
            ('annuel', 'Annuel'),
        ],
        default='trimestriel',
        verbose_name="Fréquence"
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Structure de Frais"
        verbose_name_plural = "Structures de Frais"
        ordering = ['academic_year', 'class_level', 'fee_type']
        unique_together = ['academic_year', 'class_level', 'fee_type']

    def __str__(self):
        return f"{self.fee_type.name} - {self.class_level.name} ({self.academic_year.name})"


class Enrollment(models.Model):
    """Inscription/Réinscription des étudiants"""
    ENROLLMENT_TYPE_CHOICES = [
        ('new', 'Nouvelle inscription'),
        ('renewal', 'Réinscription'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Étudiant")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Année scolaire")
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="Classe")
    enrollment_type = models.CharField(max_length=10, choices=ENROLLMENT_TYPE_CHOICES, verbose_name="Type")
    enrollment_date = models.DateField(verbose_name="Date d'inscription")
    enrollment_fee = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Frais d'inscription (FCFA)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Remarques")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['-enrollment_date', '-created_at']
        unique_together = ['student', 'academic_year']

    def __str__(self):
        return f"{self.student.name} {self.student.first_name} - {self.class_enrolled.name} ({self.academic_year.name})"


class PaymentMethod(models.Model):
    """Modes de paiement"""
    METHOD_CHOICES = [
        ('cash', 'Espèces'),
        ('bank_transfer', 'Virement bancaire'),
        ('mobile_money', 'Mobile Money'),
        ('check', 'Chèque'),
        ('card', 'Carte bancaire'),
    ]

    name = models.CharField(max_length=50, verbose_name="Nom")
    method_type = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Type")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mode de Paiement"
        verbose_name_plural = "Modes de Paiement"
        ordering = ['name']

    def __str__(self):
        return self.name


class Payment(models.Model):
    """Paiements des étudiants"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('partial', 'Partiel'),
        ('completed', 'Complet'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]

    PERIOD_CHOICES = [
        ('trimestre1', 'Trimestre 1'),
        ('trimestre2', 'Trimestre 2'),
        ('trimestre3', 'Trimestre 3'),
        ('semestre1', 'Semestre 1'),
        ('semestre2', 'Semestre 2'),
        ('annuel', 'Annuel'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Étudiant")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Année scolaire")
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, verbose_name="Type de frais")

    # Montants
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant total (FCFA)"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        default=0,
        verbose_name="Montant payé (FCFA)"
    )

    # Détails du paiement
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, verbose_name="Mode de paiement")
    payment_date = models.DateField(verbose_name="Date de paiement")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, blank=True, verbose_name="Période")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de référence")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID de transaction")

    # Statut
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Statut")

    # Informations supplémentaires
    notes = models.TextField(blank=True, verbose_name="Notes")
    received_by = models.CharField(max_length=100, blank=True, verbose_name="Reçu par")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.fee_type.name} - {self.paid_amount} FCFA"

    @property
    def remaining_amount(self):
        """Montant restant à payer"""
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        """Vérifier si entièrement payé"""
        return self.paid_amount >= self.total_amount

    @property
    def payment_percentage(self):
        """Pourcentage payé"""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0

    def save(self, *args, **kwargs):
        # Mettre à jour automatiquement le statut
        if self.paid_amount == 0:
            self.status = 'pending'
        elif self.paid_amount >= self.total_amount:
            self.status = 'completed'
        elif self.paid_amount > 0:
            self.status = 'partial'

        super().save(*args, **kwargs)


class PaymentInstallment(models.Model):
    """Versements (pour les paiements échelonnés)"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='installments', verbose_name="Paiement")
    installment_number = models.IntegerField(verbose_name="Numéro de versement")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant (FCFA)"
    )
    payment_date = models.DateField(verbose_name="Date de versement")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, verbose_name="Mode de paiement")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    received_by = models.CharField(max_length=100, blank=True, verbose_name="Reçu par")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Versement"
        verbose_name_plural = "Versements"
        ordering = ['payment', 'installment_number']

    def __str__(self):
        return f"Versement #{self.installment_number} - {self.amount} FCFA"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour le montant payé du paiement principal
        total_installments = self.payment.installments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        self.payment.paid_amount = total_installments
        self.payment.save()


class StudentAccount(models.Model):
    """Compte financier de l'étudiant"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, verbose_name="Étudiant")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Année scolaire")

    total_fees = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Total des frais (FCFA)"
    )
    total_paid = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Total payé (FCFA)"
    )

    last_payment_date = models.DateField(null=True, blank=True, verbose_name="Dernier paiement")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compte Étudiant"
        verbose_name_plural = "Comptes Étudiants"
        ordering = ['student']
        unique_together = ['student', 'academic_year']

    def __str__(self):
        return f"Compte - {self.student.name} {self.student.first_name}"

    @property
    def balance(self):
        """Solde (montant restant à payer)"""
        return self.total_fees - self.total_paid

    @property
    def payment_percentage(self):
        """Pourcentage payé"""
        if self.total_fees > 0:
            return (self.total_paid / self.total_fees) * 100
        return 0

    def update_totals(self):
        """Mettre à jour les totaux depuis les paiements"""
        payments = Payment.objects.filter(
            student=self.student,
            academic_year=self.academic_year
        )

        self.total_fees = payments.aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0')

        self.total_paid = payments.aggregate(
            total=models.Sum('paid_amount')
        )['total'] or Decimal('0')

        last_payment = payments.filter(
            paid_amount__gt=0
        ).order_by('-payment_date').first()

        if last_payment:
            self.last_payment_date = last_payment.payment_date

        self.save()


class Receipt(models.Model):
    """Reçus de paiement"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='receipts', verbose_name="Paiement")
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de reçu")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant (FCFA)"
    )
    issue_date = models.DateField(auto_now_add=True, verbose_name="Date d'émission")
    issued_by = models.CharField(max_length=100, verbose_name="Émis par")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reçu"
        verbose_name_plural = "Reçus"
        ordering = ['-issue_date']

    def __str__(self):
        return f"Reçu #{self.receipt_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Générer automatiquement le numéro de reçu
            from datetime import datetime
            year = datetime.now().year
            count = Receipt.objects.filter(
                issue_date__year=year
            ).count() + 1
            self.receipt_number = f"REC-{year}-{count:05d}"
        super().save(*args, **kwargs)
