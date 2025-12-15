from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from school_portal.models import Student, Class, Enrollment
import datetime
import json


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
    enrollments = Enrollment.objects.select_related('student', 'classe').all()

    # Filtres
    search = request.GET.get('search', '')
    enrollment_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if search:
        enrollments = enrollments.filter(
            student__name__icontains=search
        ) | enrollments.filter(
            student__first_name__icontains=search
        ) | enrollments.filter(
            student__matricule__icontains=search
        )

    if enrollment_type:
        enrollments = enrollments.filter(enrollment_type=enrollment_type)

    if status:
        enrollments = enrollments.filter(status=status)

    context = {
        'enrollments': enrollments,
        'total_enrollments': Enrollment.objects.count(),
        'new_enrollments': Enrollment.objects.filter(enrollment_type='inscription').count(),
        'reinrollments': Enrollment.objects.filter(enrollment_type='reinscription').count(),
    }
    return render(request, 'finance/enrollments_list.html', context)


@login_required
def enrollment_create(request):
    """Créer une nouvelle inscription (avec création d'élève si nécessaire)"""
    if request.method == 'POST':
        try:
            enrollment_type = request.POST.get('enrollment_type')

            # Réinscription : chercher l'élève par matricule
            if enrollment_type == 'reinscription':
                matricule = request.POST.get('matricule')
                if not matricule:
                    messages.error(request, 'Le matricule est requis pour une réinscription')
                    return redirect('enrollment_create')

                try:
                    student = Student.objects.get(matricule=matricule)
                except Student.DoesNotExist:
                    messages.error(request, f'Aucun élève trouvé avec le matricule {matricule}')
                    return redirect('enrollment_create')

            # Nouvelle inscription : créer l'élève
            else:
                student = Student.objects.create(
                    name=request.POST.get('name'),
                    first_name=request.POST.get('first_name'),
                    surname=request.POST.get('surname', ''),
                    birth_date=request.POST.get('birth_date'),
                    email=request.POST.get('email', ''),
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address')
                )

            # Créer l'inscription
            classe = Class.objects.get(id=request.POST.get('classe'))

            # Gérer le montant optionnel
            amount = request.POST.get('amount', '')
            amount = float(amount) if amount else None

            enrollment = Enrollment.objects.create(
                student=student,
                classe=classe,
                enrollment_type=enrollment_type,
                academic_year=request.POST.get('academic_year'),
                amount=amount,
                enrollment_date=request.POST.get('enrollment_date'),
                status=request.POST.get('status', 'completed'),
                payment_method=request.POST.get('payment_method', ''),
                reference=request.POST.get('reference', ''),
                notes=request.POST.get('notes', '')
            )

            # Assigner l'élève à la classe
            classe.students.add(student)

            messages.success(
                request,
                f'Inscription enregistrée avec succès ! Matricule: {student.matricule}'
            )
            return redirect('enrollments_list')

        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('enrollment_create')

    classes = Class.objects.all()
    current_year = datetime.date.today().year
    academic_year = f"{current_year}-{current_year + 1}"

    context = {
        'classes': classes,
        'academic_year': academic_year
    }
    return render(request, 'finance/enrollment_form.html', context)


@login_required
def get_student_by_matricule(request):
    """API pour récupérer les infos d'un élève par matricule (AJAX)"""
    matricule = request.GET.get('matricule', '')

    try:
        student = Student.objects.get(matricule=matricule)
        data = {
            'success': True,
            'student': {
                'matricule': student.matricule,
                'name': student.name,
                'first_name': student.first_name,
                'surname': student.surname or '',
                'birth_date': student.birth_date.strftime('%Y-%m-%d'),
                'email': student.email or '',
                'phone': student.phone,
                'address': student.address,
                'classe': student.classe.name if student.classe else ''
            }
        }
    except Student.DoesNotExist:
        data = {
            'success': False,
            'message': 'Aucun élève trouvé avec ce matricule'
        }

    return JsonResponse(data)


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
