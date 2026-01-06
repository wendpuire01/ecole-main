from django.db import models
from django.db.models import Avg
import datetime


# Students Model
class Student(models.Model):
    matricule = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(null=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20,blank=True, null=True)
    address = models.CharField(max_length=200,blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Student: {self.name}>"

    def save(self, *args, **kwargs):
        """Génère automatiquement le matricule si vide"""
        if not self.matricule:
            # Format: ET-YYYY-NNNN (ET = Étudiant, YYYY = année, NNNN = numéro séquentiel)
            current_year = datetime.date.today().year
            # Compte les étudiants de cette année
            last_student = Student.objects.filter(
                matricule__startswith=f'ET-{current_year}'
            ).order_by('matricule').last()

            if last_student and last_student.matricule:
                # Extraire le numéro et incrémenter
                last_num = int(last_student.matricule.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.matricule = f'ET-{current_year}-{new_num:04d}'

        super().save(*args, **kwargs)

    def age(self):
        return int((datetime.date.today() - self.birth_date).days / 365.25)

    @property
    def classe(self):
        """Retourne la classe de l'étudiant"""
        return self.class_set.first()

    def get_average(self, period=None, subject=None):
        """Calcule la moyenne de l'étudiant avec coefficients des matières (uniquement devoirs et compositions)"""
        marks = Mark.objects.filter(student=self)

        # Filtrer uniquement les devoirs et compositions
        marks = marks.filter(assignment__evaluation_type__in=['devoir', 'composition', 'Composition'])

        if period:
            marks = marks.filter(assignment__period=period)
        if subject:
            marks = marks.filter(assignment__subject=subject)

        if not marks.exists():
            return None

        # Récupérer la classe de l'étudiant
        classe = self.classe

        # Si on calcule pour UNE matière spécifique
        if subject:
            total_points = 0
            total_marks = 0

            for mark in marks:
                total_points += mark.score
                total_marks += 1

            if total_marks == 0:
                return None

            return round(total_points / total_marks, 2)

        # Si on calcule la moyenne GÉNÉRALE (toutes matières)
        # Calculer d'abord la moyenne par matière, puis pondérer par coefficient matière
        subjects_averages = {}

        for mark in marks:
            subject_name = mark.assignment.subject.name
            if subject_name not in subjects_averages:
                subjects_averages[subject_name] = {
                    'subject': mark.assignment.subject,
                    'total_points': 0,
                    'total_marks': 0,
                }

            subjects_averages[subject_name]['total_points'] += mark.score
            subjects_averages[subject_name]['total_marks'] += 1

        # Calculer la moyenne générale pondérée par coefficient matière
        total_weighted_points = 0
        total_subject_coefficients = 0

        for subject_data in subjects_averages.values():
            if subject_data['total_marks'] > 0:
                # Moyenne de la matière
                subject_avg = subject_data['total_points'] / subject_data['total_marks']

                # Coefficient de la matière pour cette classe
                subject_coef = 1  # Par défaut
                if classe:
                    subject_coef = subject_data['subject'].get_coefficient_for_class(classe)

                total_weighted_points += subject_avg * subject_coef
                total_subject_coefficients += subject_coef

        if total_subject_coefficients == 0:
            return None

        return round(total_weighted_points / total_subject_coefficients, 2)

    def get_subject_average(self, subject, period=None):
        """Calcule la moyenne pour une matière"""
        return self.get_average(period=period, subject=subject)

    def get_rank_in_class(self, period=None):
        """Retourne le rang de l'étudiant dans sa classe avec gestion des ex-aequo"""
        classe = self.classe
        if not classe:
            return None

        students_averages = []
        for student in classe.students.all():
            avg = student.get_average(period=period)
            if avg is not None:
                students_averages.append({'student': student, 'average': avg})

        if not students_averages:
            return None

        # Trier par moyenne décroissante
        students_averages.sort(key=lambda x: x['average'], reverse=True)

        # Calculer le rang avec gestion des ex-aequo
        current_rank = 1
        for i, item in enumerate(students_averages):
            # Si ce n'est pas le premier et que la moyenne est différente de la précédente
            if i > 0 and item['average'] < students_averages[i-1]['average']:
                current_rank = i + 1

            # Trouver le rang de cet étudiant
            if item['student'].id == self.id:
                return current_rank

        return None


# Teachers Model
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True,null=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Teacher: {self.name} {self.first_name}>"

    def age(self):
        return int((datetime.date.today() - self.birth_date).days / 365.25)


# Classes Model
class Class(models.Model):
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    students = models.ManyToManyField(Student, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Class: {self.name}>"

    def students_count(self):
        return self.students.count()

    def get_students_rankings(self, period=None):
        """Calcule les rangs de tous les élèves de la classe en une seule fois
        Retourne un dictionnaire {student_id: rank}
        """
        students_averages = []
        for student in self.students.all():
            avg = student.get_average(period=period)
            if avg is not None:
                students_averages.append({'student_id': student.id, 'average': avg})

        if not students_averages:
            return {}

        # Trier par moyenne décroissante
        students_averages.sort(key=lambda x: x['average'], reverse=True)

        # Calculer les rangs avec gestion des ex-aequo
        rankings = {}
        current_rank = 1
        for i, item in enumerate(students_averages):
            # Si ce n'est pas le premier et que la moyenne est différente de la précédente
            if i > 0 and item['average'] < students_averages[i-1]['average']:
                current_rank = i + 1

            rankings[item['student_id']] = current_rank

        return rankings


# Subjects Model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    classes = models.ManyToManyField(Class, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Subject: {self.name}>"

    def classes_count(self):
        return self.classes.count()

    def get_coefficient_for_class(self, classe):
        """Retourne le coefficient de la matière pour une classe donnée"""
        try:
            subject_class = SubjectClass.objects.get(subject=self, classe=classe)
            return subject_class.coefficient
        except SubjectClass.DoesNotExist:
            return 1  # Coefficient par défaut

    def get_teacher_for_class(self, classe):
        """Retourne l'enseignant de la matière pour une classe donnée"""
        try:
            subject_class = SubjectClass.objects.get(subject=self, classe=classe)
            return subject_class.teacher if subject_class.teacher else self.teacher
        except SubjectClass.DoesNotExist:
            return self.teacher  # Enseignant par défaut


# Table pour gérer les coefficients et enseignants par matière/classe
class SubjectClass(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_classes')
    classe = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subject_classes')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='subject_classes')
    coefficient = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['subject', 'classe']
        verbose_name = 'Matière-Classe'
        verbose_name_plural = 'Matières-Classes'

    def __str__(self):
        teacher_name = f" - {self.teacher.name}" if self.teacher else ""
        return f"{self.subject.name} - {self.classe.name}{teacher_name} (Coef: {self.coefficient})"


# Période/Trimestre Model
class Period(models.Model):
    PERIOD_CHOICES = [
        ('trimestre1', '1er Trimestre'),
        ('trimestre2', '2e Trimestre'),
        ('trimestre3', '3e Trimestre'),
        ('semestre1', '1er Semestre'),
        ('semestre2', '2e Semestre'),
    ]

    name = models.CharField(max_length=50, choices=PERIOD_CHOICES)
    academic_year = models.CharField(max_length=20)  # Ex: 2024-2025
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'academic_year']
        ordering = ['-academic_year', 'start_date']

    def __str__(self):
        return f"{self.get_name_display()} - {self.academic_year}"


# Assigment Model
class Assignment(models.Model):
    EVALUATION_TYPES = [
        ('devoir', 'Devoir'),
        ('composition', 'Composition'),
        ('interrogation', 'Interrogation'),
        ('examen', 'Examen'),
        ('tp', 'Travaux Pratiques'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True)
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPES, default='devoir')
    due_date = models.DateField()
    points = models.IntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Marks Model
class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    date = models.DateField()
    score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.name + ' ' + self.subject + ' ' + self.assignment + ' ' + str(self.score)


# Enrollment Model - Historique des inscriptions
class Enrollment(models.Model):
    ENROLLMENT_TYPES = [
        ('inscription', 'Nouvelle Inscription'),
        ('reinscription', 'Réinscription'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complétée'),
        ('cancelled', 'Annulée'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('bank', 'Virement Bancaire'),
        ('mobile', 'Mobile Money'),
        ('check', 'Chèque'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    classe = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_type = models.CharField(max_length=20, choices=ENROLLMENT_TYPES, default='inscription')
    academic_year = models.CharField(max_length=20)  # Ex: 2024-2025
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    enrollment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-enrollment_date', '-created_at']
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'

    def __str__(self):
        return f"{self.student.matricule} - {self.classe.name} ({self.academic_year})"


# Paramètres de l'École
class SchoolSettings(models.Model):
    """Paramètres globaux de l'école (nom, logo, contacts)"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'école")
    address = models.CharField(max_length=300, verbose_name="Adresse")
    phone = models.CharField(max_length=50, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Site web")
    logo = models.ImageField(upload_to='school_logo/', blank=True, null=True, verbose_name="Logo de l'école")

    # Informations complémentaires
    director_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom du Directeur")
    motto = models.CharField(max_length=300, blank=True, null=True, verbose_name="Devise de l'école")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres de l'École"
        verbose_name_plural = "Paramètres de l'École"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """S'assurer qu'il n'y a qu'une seule instance de paramètres"""
        if not self.pk and SchoolSettings.objects.exists():
            # Si une instance existe déjà, la mettre à jour au lieu de créer une nouvelle
            existing = SchoolSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)



