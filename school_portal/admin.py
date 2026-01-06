from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Teacher, Class, Subject, SubjectClass, Period, Assignment, Mark, SchoolSettings


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'birth_date', 'age_display', 'email', 'phone', 'created_at']
    list_filter = ['birth_date', 'created_at']
    search_fields = ['name', 'first_name', 'surname', 'email', 'phone']
    date_hierarchy = 'created_at'
    ordering = ['name', 'first_name']

    def full_name(self, obj):
        return f"{obj.name} {obj.first_name} {obj.surname}"
    full_name.short_description = 'Nom Complet'

    def age_display(self, obj):
        return f"{obj.age()} ans"
    age_display.short_description = 'Âge'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'birth_date', 'age_display', 'email', 'phone', 'created_at']
    list_filter = ['birth_date', 'created_at']
    search_fields = ['name', 'first_name', 'surname', 'email', 'phone']
    date_hierarchy = 'created_at'
    ordering = ['name', 'first_name']

    def full_name(self, obj):
        return f"{obj.name} {obj.first_name} {obj.surname}"
    full_name.short_description = 'Nom Complet'

    def age_display(self, obj):
        return f"{obj.age()} ans"
    age_display.short_description = 'Âge'


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'teacher', 'students_count_display', 'created_at']
    list_filter = ['level', 'teacher', 'created_at']
    search_fields = ['name', 'level']
    filter_horizontal = ['students']
    date_hierarchy = 'created_at'
    ordering = ['name']

    def students_count_display(self, obj):
        count = obj.students_count()
        return format_html('<strong>{}</strong> élèves', count)
    students_count_display.short_description = 'Effectif'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'classes_count_display', 'created_at']
    list_filter = ['teacher', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['classes']
    date_hierarchy = 'created_at'
    ordering = ['name']

    def classes_count_display(self, obj):
        count = obj.classes_count()
        return format_html('<strong>{}</strong> classes', count)
    classes_count_display.short_description = 'Nombre de classes'


@admin.register(SubjectClass)
class SubjectClassAdmin(admin.ModelAdmin):
    list_display = ['subject', 'classe', 'teacher', 'coefficient', 'created_at']
    list_filter = ['subject', 'classe', 'teacher']
    search_fields = ['subject__name', 'classe__name', 'teacher__name']
    ordering = ['classe', 'subject']
    autocomplete_fields = ['subject', 'classe', 'teacher']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name_display', 'academic_year', 'start_date', 'end_date', 'is_active_display', 'created_at']
    list_filter = ['name', 'academic_year', 'is_active']
    search_fields = ['academic_year']
    date_hierarchy = 'start_date'
    ordering = ['-academic_year', 'start_date']

    def name_display(self, obj):
        return obj.get_name_display()
    name_display.short_description = 'Période'

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: gray;">Inactive</span>')
    is_active_display.short_description = 'Statut'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'evaluation_type_display', 'period', 'due_date', 'points', 'created_at']
    list_filter = ['subject', 'evaluation_type', 'period', 'due_date', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'due_date'
    ordering = ['-due_date']

    def evaluation_type_display(self, obj):
        colors = {
            'devoir': 'blue',
            'composition': 'purple',
            'interrogation': 'orange',
            'examen': 'red',
            'tp': 'green',
        }
        color = colors.get(obj.evaluation_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_evaluation_type_display()
        )
    evaluation_type_display.short_description = 'Type'


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'assignment', 'score_display', 'date', 'created_at']
    list_filter = ['assignment__subject', 'date', 'created_at']
    search_fields = ['student__name', 'student__first_name', 'assignment__name']
    date_hierarchy = 'date'
    ordering = ['-date', 'student']

    def student_name(self, obj):
        return f"{obj.student.name} {obj.student.first_name}"
    student_name.short_description = 'Étudiant'

    def score_display(self, obj):
        color = 'green' if obj.score >= 10 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}/20</span>', color, obj.score)
    score_display.short_description = 'Note'


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'address', 'phone', 'email', 'website')
        }),
        ('Branding', {
            'fields': ('logo', 'motto')
        }),
        ('Direction', {
            'fields': ('director_name',)
        }),
    )

    def has_add_permission(self, request):
        # Empêcher la création de plus d'une instance
        return not SchoolSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False
