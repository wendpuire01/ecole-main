from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from school_portal.models import Student, Class


# ===================================
# PAYMENTS VIEWS
# ===================================

@login_required
def payments_list(request):
    """Liste de tous les paiements"""

    # Données simulées pour l'instant
    # À remplacer par de vraies données une fois le modèle Payment créé
    payments = [
        {
            'id': 1,
            'student_name': 'Jean KABORE',
            'student_id': 'ET-0001',
            'class_name': 'Terminale S1',
            'type': 'Scolarité',
            'total_amount': 300000,
            'paid_amount': 300000,
            'remaining': 0,
            'date': '2024-12-14',
            'status': 'paid'
        },
        {
            'id': 2,
            'student_name': 'Marie TRAORE',
            'student_id': 'ET-0002',
            'class_name': 'Première L2',
            'type': 'Inscription',
            'total_amount': 250000,
            'paid_amount': 150000,
            'remaining': 100000,
            'date': '2024-12-10',
            'status': 'pending'
        },
        {
            'id': 3,
            'student_name': 'Paul OUEDRAOGO',
            'student_id': 'ET-0003',
            'class_name': 'Seconde A',
            'type': 'Scolarité',
            'total_amount': 300000,
            'paid_amount': 0,
            'remaining': 300000,
            'date': '2024-12-01',
            'status': 'unpaid'
        },
    ]

    # Statistiques
    total_received = sum(p['paid_amount'] for p in payments)
    total_pending = sum(p['remaining'] for p in payments if p['status'] == 'pending')
    total_unpaid = sum(p['total_amount'] for p in payments if p['status'] == 'unpaid')
    monthly_total = sum(p['paid_amount'] for p in payments)

    classes = Class.objects.all()
    students = Student.objects.all()

    context = {
        'payments': payments,
        'classes': classes,
        'students': students,
        'total_received': f'{total_received/1000000:.1f}M',
        'total_pending': f'{total_pending/1000000:.1f}M',
        'total_unpaid': f'{total_unpaid/1000000:.1f}M',
        'monthly_total': f'{monthly_total/1000000:.1f}M',
    }
    return render(request, 'finance/payments_list.html', context)


@login_required
def payment_create(request):
    """Créer un nouveau paiement"""
    if request.method == 'POST':
        try:
            # Logique de création de paiement
            # À implémenter avec le modèle Payment
            messages.success(request, 'Paiement enregistré avec succès')
            return redirect('payments_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    students = Student.objects.all()
    context = {'students': students}
    return render(request, 'finance/payment_form.html', context)


@login_required
def payment_detail(request, pk):
    """Détails d'un paiement"""
    # À implémenter
    context = {'payment_id': pk}
    return render(request, 'finance/payment_detail.html', context)


@login_required
def payment_edit(request, pk):
    """Modifier un paiement"""
    if request.method == 'POST':
        messages.success(request, 'Paiement modifié avec succès')
        return redirect('payments_list')

    context = {'payment_id': pk}
    return render(request, 'finance/payment_form.html', context)


# ===================================
# ENROLLMENTS VIEWS
# ===================================

@login_required
def enrollments_list(request):
    """Liste des inscriptions"""

    # Données simulées
    enrollments = [
        {
            'id': 1,
            'student_name': 'Jean KABORE',
            'class_name': 'Terminale S1',
            'type': 'Réinscription',
            'amount': 200000,
            'date': '2024-09-01',
            'status': 'completed'
        },
        {
            'id': 2,
            'student_name': 'Marie TRAORE',
            'class_name': 'Première L2',
            'type': 'Inscription',
            'amount': 250000,
            'date': '2024-09-05',
            'status': 'pending'
        },
    ]

    context = {
        'enrollments': enrollments,
        'total_enrollments': len(enrollments),
    }
    return render(request, 'finance/enrollments_list.html', context)


@login_required
def enrollment_create(request):
    """Créer une nouvelle inscription"""
    if request.method == 'POST':
        try:
            messages.success(request, 'Inscription enregistrée avec succès')
            return redirect('enrollments_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    students = Student.objects.all()
    classes = Class.objects.all()
    context = {'students': students, 'classes': classes}
    return render(request, 'finance/enrollment_form.html', context)


# ===================================
# REPORTS VIEWS
# ===================================

@login_required
def finance_reports(request):
    """Rapports financiers"""

    # Statistiques pour le rapport
    total_revenue = 8500000
    total_expenses = 2000000
    net_profit = total_revenue - total_expenses

    monthly_data = [
        {'month': 'Janvier', 'revenue': 1200000, 'expenses': 300000},
        {'month': 'Février', 'revenue': 1500000, 'expenses': 350000},
        {'month': 'Mars', 'revenue': 1800000, 'expenses': 400000},
        {'month': 'Avril', 'revenue': 1400000, 'expenses': 320000},
        {'month': 'Mai', 'revenue': 1600000, 'expenses': 380000},
        {'month': 'Juin', 'revenue': 1000000, 'expenses': 250000},
    ]

    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'monthly_data': monthly_data,
    }
    return render(request, 'finance/reports.html', context)


@login_required
def receipt(request, payment_id):
    """Reçu de paiement"""

    # Données simulées
    payment = {
        'id': payment_id,
        'receipt_number': f'REC-2024-{payment_id:05d}',
        'student_name': 'Jean KABORE',
        'class_name': 'Terminale S1',
        'amount': 300000,
        'payment_method': 'Espèces',
        'date': '2024-12-14',
        'description': 'Paiement scolarité - Trimestre 1',
    }

    context = {
        'payment': payment,
        'school_name': 'ÉCOLE SECONDAIRE',
        'school_address': 'Ouagadougou, Burkina Faso',
        'school_phone': '+226 XX XX XX XX',
    }
    return render(request, 'finance/receipt.html', context)
