from django.urls import path
from . import views

urlpatterns = [
    # Students
    path('students/', views.students_list, name='students_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    # Classes
    path('classes/', views.classes_list, name='classes_list'),
    path('classes/create/', views.class_create, name='classes_create'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    path('classes/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('classes/<int:pk>/assign-students/', views.assign_students, name='assign_students'),
    path('classes/<int:pk>/students/', views.class_students, name='class_students'),
    path('classes/<int:pk>/grades/', views.class_grades, name='class_grades'),

    # Teachers
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),

    # Subjects
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Grades
    path('grades/', views.grades_list, name='grades_list'),
    path('grades/save/', views.save_grade, name='save_grade'),
    path('grades/<int:mark_id>/delete/', views.delete_grade, name='delete_grade'),
    path('grades/calculate-averages/', views.calculate_averages, name='calculate_averages'),
    path('grades/generate-bulletins/', views.generate_bulletins, name='generate_bulletins'),

    # Reports
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:student_id>/', views.report_card, name='report_card_old'),  # Ancien format pour compatibilité
    path('report-card/<int:student_id>/', views.report_card, name='report_card'),
    path('bulk-report-cards/', views.bulk_report_cards, name='bulk_report_cards'),

    # Periods Management
    path('periods/', views.periods_list, name='periods_list'),
    path('periods/create/', views.period_create, name='period_create'),
    path('periods/<int:period_id>/edit/', views.period_edit, name='period_edit'),
    path('periods/<int:period_id>/delete/', views.period_delete, name='period_delete'),
    path('periods/<int:period_id>/activate/', views.activate_period, name='activate_period'),
]
