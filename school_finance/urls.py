from django.urls import path
from . import views

urlpatterns = [
    # Payments
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/versement/', views.add_installment, name='add_installment'),

    # Student account
    path('eleve/<int:student_id>/compte/', views.student_account, name='student_account'),

    # Enrollments
    path('enrollments/', views.enrollments_list, name='enrollments_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),

    # AJAX
    path('api/student-by-matricule/', views.get_student_by_matricule, name='get_student_by_matricule'),
    path('api/students/search/', views.search_students_api, name='search_students_api'),
    path('api/schedule-amount/', views.get_schedule_amount, name='get_schedule_amount'),
    path('api/fee-structures/', views.get_fee_structures, name='get_fee_structures'),

    # Reports & Receipt
    path('reports/', views.finance_reports, name='finance_reports'),
    path('recu/<str:receipt_number>/', views.receipt_view, name='receipt_view'),

    # Settings CRUD
    path('settings/annee/create/',               views.academic_year_create,    name='academic_year_create'),
    path('settings/annee/<int:pk>/edit/',         views.academic_year_edit,      name='academic_year_edit'),
    path('settings/annee/<int:pk>/delete/',       views.academic_year_delete,    name='academic_year_delete'),

    path('settings/type-frais/create/',           views.fee_type_create,         name='fee_type_create'),
    path('settings/type-frais/<int:pk>/edit/',    views.fee_type_edit,           name='fee_type_edit'),
    path('settings/type-frais/<int:pk>/delete/',  views.fee_type_delete,         name='fee_type_delete'),

    path('settings/mode-paiement/create/',               views.payment_method_create,    name='payment_method_create'),
    path('settings/mode-paiement/<int:pk>/edit/',         views.payment_method_edit,      name='payment_method_edit'),
    path('settings/mode-paiement/<int:pk>/delete/',       views.payment_method_delete,    name='payment_method_delete'),

    path('settings/frais/create/',               views.fee_structure_create,    name='fee_structure_create'),
    path('settings/frais/<int:pk>/edit/',         views.fee_structure_edit,      name='fee_structure_edit'),
    path('settings/frais/<int:pk>/delete/',       views.fee_structure_delete,    name='fee_structure_delete'),
]
