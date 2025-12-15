from django.urls import path
from . import views

urlpatterns = [
    # Payments
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),

    # Enrollments
    path('enrollments/', views.enrollments_list, name='enrollments_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),

    # Reports
    path('reports/', views.finance_reports, name='finance_reports'),
    path('receipt/<int:payment_id>/', views.receipt, name='receipt'),
]
