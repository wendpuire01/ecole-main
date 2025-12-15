from django.db import models
from django.db.models import Avg
import datetime


# Students Model
class Student(models.Model):
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField()
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Student: {self.name}>"

    def age(self):
        return int((datetime.date.today() - self.birth_date).days / 365.25)

    @property
    def classe(self):
        """Retourne la classe de l'étudiant"""
        return self.class_set.first()

    def get_average(self, period=None, subject=None):
        """Calcule la moyenne de l'étudiant"""
        marks = Mark.objects.filter(student=self)

        if period:
            marks = marks.filter(assignment__period=period)
        if subject:
            marks = marks.filter(assignment__subject=subject)

        if not marks.exists():
            return None

        total_points = 0
        total_coefficients = 0

        for mark in marks:
            coefficient = mark.assignment.coefficient
            total_points += mark.score * coefficient
            total_coefficients += coefficient

        if total_coefficients == 0:
            return None

        return round(total_points / total_coefficients, 2)

    def get_subject_average(self, subject, period=None):
        """Calcule la moyenne pour une matière"""
        return self.get_average(period=period, subject=subject)

    def get_rank_in_class(self, period=None):
        """Retourne le rang de l'étudiant dans sa classe"""
        classe = self.classe
        if not classe:
            return None

        students_averages = []
        for student in classe.students.all():
            avg = student.get_average(period=period)
            if avg is not None:
                students_averages.append({'student': student, 'average': avg})

        # Trier par moyenne décroissante
        students_averages.sort(key=lambda x: x['average'], reverse=True)

        # Trouver le rang
        for rank, item in enumerate(students_averages, 1):
            if item['student'].id == self.id:
                return rank

        return None


# Teachers Model
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField()
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Teacher: {self.name}>"

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


# Table pour gérer les coefficients par matière/classe
class SubjectClass(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_classes')
    classe = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subject_classes')
    coefficient = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['subject', 'classe']
        verbose_name = 'Matière-Classe'
        verbose_name_plural = 'Matières-Classes'

    def __str__(self):
        return f"{self.subject.name} - {self.classe.name} (Coef: {self.coefficient})"


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
    coefficient = models.IntegerField(default=1)

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



