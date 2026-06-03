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
    path('api/schedule-amount/', views.get_schedule_amount, name='get_schedule_amount'),
    path('api/fee-structures/', views.get_fee_structures, name='get_fee_structures'),

    # Reports & Receipt
    path('reports/', views.finance_reports, name='finance_reports'),
    path('recu/<str:receipt_number>/', views.receipt_view, name='receipt_view'),
]
