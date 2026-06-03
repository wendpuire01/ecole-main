from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
import datetime

from school_portal.models import Student, Class, Enrollment as PortalEnrollment, SchoolSettings
from .models import (
    AcademicYear, FeeType, FeeStructure, PaymentSchedule,
    PaymentMethod, Payment, PaymentInstallment,
    StudentAccount, Receipt, Enrollment as FinanceEnrollment,
)


# ===================================
# PAYMENTS VIEWS
# ===================================

@login_required
def payments_list(request):
    active_year = AcademicYear.objects.filter(is_active=True).first()
    year_id = request.GET.get('year', '')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    fee_category = request.GET.get('type', '')
    class_id = request.GET.get('class', '')
    period = request.GET.get('period', '')

    payments = Payment.objects.select_related(
        'student', 'fee_type', 'academic_year', 'payment_method'
    ).order_by('-payment_date', '-created_at')

    if year_id:
        payments = payments.filter(academic_year_id=year_id)
    elif active_year:
        payments = payments.filter(academic_year=active_year)

    if search:
        payments = payments.filter(
            Q(student__name__icontains=search) |
            Q(student__first_name__icontains=search) |
            Q(student__matricule__icontains=search)
        )
    if status:
        payments = payments.filter(status=status)
    if fee_category:
        payments = payments.filter(fee_type__category=fee_category)
    if period:
        payments = payments.filter(period=period)
    if class_id:
        payments = payments.filter(student__class_set__id=class_id)

    stats = payments.aggregate(
        total_received=Sum('paid_amount'),
        total_due=Sum('total_amount'),
    )
    total_received = stats['total_received'] or Decimal('0')
    total_due = stats['total_due'] or Decimal('0')
    total_remaining = total_due - total_received

    today = timezone.now().date()
    month_start = today.replace(day=1)
    monthly_total = payments.filter(
        payment_date__gte=month_start
    ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')

    pending_count = payments.filter(status__in=['pending', 'partial']).count()

    context = {
        'payments': payments,
        'classes': Class.objects.all(),
        'academic_years': AcademicYear.objects.all(),
        'fee_types': FeeType.objects.filter(is_active=True),
        'active_year': active_year,
        'total_received': total_received,
        'total_remaining': total_remaining,
        'pending_count': pending_count,
        'monthly_total': monthly_total,
        'search': search,
        'selected_status': status,
        'selected_type': fee_category,
        'selected_class': class_id,
        'selected_period': period,
        'selected_year': year_id,
    }
    return render(request, 'finance/payments_list.html', context)


@login_required
def payment_create(request):
    if request.method == 'POST':
        try:
            student = get_object_or_404(Student, pk=request.POST.get('student'))
            fee_type = get_object_or_404(FeeType, pk=request.POST.get('fee_type'))
            academic_year = get_object_or_404(AcademicYear, pk=request.POST.get('academic_year'))
            payment_method = get_object_or_404(PaymentMethod, pk=request.POST.get('payment_method'))

            total_amount = Decimal(request.POST.get('total_amount', '0'))
            paid_amount = Decimal(request.POST.get('paid_amount', '0'))
            payment_date = request.POST.get('payment_date')
            period = request.POST.get('period', '')
            received_by = request.POST.get('received_by', '')
            reference = request.POST.get('reference', '')
            notes = request.POST.get('notes', '')

            if paid_amount > total_amount:
                messages.error(request, 'Le montant versé ne peut pas dépasser le montant total.')
                return redirect('payment_create')

            payment = Payment.objects.create(
                student=student,
                academic_year=academic_year,
                fee_type=fee_type,
                total_amount=total_amount,
                paid_amount=Decimal('0'),
                payment_method=payment_method,
                payment_date=payment_date,
                period=period,
                reference_number=reference,
                received_by=received_by,
                notes=notes,
            )

            installment = PaymentInstallment.objects.create(
                payment=payment,
                installment_number=1,
                amount=paid_amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference_number=reference,
                received_by=received_by,
            )

            receipt = Receipt.objects.create(
                payment=payment,
                installment=installment,
                amount=paid_amount,
                issued_by=request.user.get_full_name() or request.user.username,
            )

            _update_student_account(student, academic_year)

            messages.success(
                request,
                f'Paiement enregistré. Reçu N° {receipt.receipt_number}'
            )
            return redirect('payment_detail', pk=payment.pk)

        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('payment_create')

    active_year = AcademicYear.objects.filter(is_active=True).first()
    context = {
        'students': Student.objects.all().order_by('name', 'first_name'),
        'fee_types': FeeType.objects.filter(is_active=True),
        'academic_years': AcademicYear.objects.all(),
        'payment_methods': PaymentMethod.objects.filter(is_active=True),
        'active_year': active_year,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
    }
    return render(request, 'finance/payment_form.html', context)


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related('student', 'fee_type', 'academic_year', 'payment_method'),
        pk=pk
    )
    installments = payment.installments.select_related('payment_method', 'receipts').order_by('installment_number')
    receipts = payment.receipts.order_by('-issue_date')

    school = SchoolSettings.objects.first()
    context = {
        'payment': payment,
        'installments': installments,
        'receipts': receipts,
        'school': school,
        'payment_methods': PaymentMethod.objects.filter(is_active=True),
        'today': timezone.now().date().strftime('%Y-%m-%d'),
    }
    return render(request, 'finance/payment_detail.html', context)


@login_required
def add_installment(request, pk):
    """Ajouter un versement à un paiement existant"""
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            payment_method = get_object_or_404(PaymentMethod, pk=request.POST.get('payment_method'))
            payment_date = request.POST.get('payment_date')
            reference = request.POST.get('reference', '')
            received_by = request.POST.get('received_by', '')
            notes = request.POST.get('notes', '')

            remaining = payment.remaining_amount
            if amount > remaining:
                messages.error(request, f'Montant trop élevé. Reste à payer: {remaining:,.0f} FCFA')
                return redirect('payment_detail', pk=pk)

            next_number = payment.installments.count() + 1
            installment = PaymentInstallment.objects.create(
                payment=payment,
                installment_number=next_number,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference_number=reference,
                received_by=received_by,
                notes=notes,
            )

            receipt = Receipt.objects.create(
                payment=payment,
                installment=installment,
                amount=amount,
                issued_by=request.user.get_full_name() or request.user.username,
            )

            _update_student_account(payment.student, payment.academic_year)

            messages.success(
                request,
                f'Versement #{next_number} enregistré. Reçu N° {receipt.receipt_number}'
            )
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    return redirect('payment_detail', pk=pk)


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        try:
            payment.notes = request.POST.get('notes', '')
            payment.received_by = request.POST.get('received_by', '')
            payment.reference_number = request.POST.get('reference', '')
            payment.save()
            messages.success(request, 'Paiement modifié avec succès')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
        return redirect('payment_detail', pk=pk)

    context = {'payment': payment}
    return render(request, 'finance/payment_form.html', context)


@login_required
def receipt_view(request, receipt_number):
    """Afficher/imprimer un reçu"""
    receipt = get_object_or_404(
        Receipt.objects.select_related(
            'payment__student', 'payment__fee_type',
            'payment__academic_year', 'installment__payment_method',
            'payment__payment_method'
        ),
        receipt_number=receipt_number
    )
    school = SchoolSettings.objects.first()
    context = {
        'receipt': receipt,
        'school': school,
    }
    return render(request, 'finance/receipt.html', context)


# ===================================
# ENROLLMENTS VIEWS
# ===================================

@login_required
def enrollments_list(request):
    enrollments = PortalEnrollment.objects.select_related('student', 'classe').all()

    search = request.GET.get('search', '')
    enrollment_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if search:
        enrollments = enrollments.filter(
            Q(student__name__icontains=search) |
            Q(student__first_name__icontains=search) |
            Q(student__matricule__icontains=search)
        )
    if enrollment_type:
        enrollments = enrollments.filter(enrollment_type=enrollment_type)
    if status:
        enrollments = enrollments.filter(status=status)

    context = {
        'enrollments': enrollments,
        'total_enrollments': PortalEnrollment.objects.count(),
        'new_enrollments': PortalEnrollment.objects.filter(enrollment_type='inscription').count(),
        'reinrollments': PortalEnrollment.objects.filter(enrollment_type='reinscription').count(),
    }
    return render(request, 'finance/enrollments_list.html', context)


@login_required
def enrollment_create(request):
    if request.method == 'POST':
        try:
            enrollment_type = request.POST.get('enrollment_type')

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

            classe = Class.objects.get(id=request.POST.get('classe'))
            amount_raw = request.POST.get('amount', '')
            amount = float(amount_raw) if amount_raw else None

            PortalEnrollment.objects.create(
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

            classe.students.add(student)

            messages.success(
                request,
                f'Inscription enregistrée. Matricule: {student.matricule}'
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
        'academic_year': academic_year,
    }
    return render(request, 'finance/enrollment_form.html', context)


# ===================================
# AJAX ENDPOINTS
# ===================================

@login_required
def get_student_by_matricule(request):
    matricule = request.GET.get('matricule', '')
    try:
        student = Student.objects.get(matricule=matricule)
        classe = student.class_set.first()
        data = {
            'success': True,
            'student': {
                'id': student.id,
                'matricule': student.matricule,
                'name': student.name,
                'first_name': student.first_name,
                'surname': student.surname or '',
                'birth_date': student.birth_date.strftime('%Y-%m-%d') if student.birth_date else '',
                'email': student.email or '',
                'phone': student.phone or '',
                'address': student.address or '',
                'classe': classe.name if classe else '',
                'classe_id': classe.id if classe else None,
            }
        }
    except Student.DoesNotExist:
        data = {'success': False, 'message': 'Aucun élève trouvé avec ce matricule'}

    return JsonResponse(data)


@login_required
def get_schedule_amount(request):
    """Retourne le montant attendu depuis l'échéancier (AJAX)"""
    class_id = request.GET.get('class_id')
    fee_type_id = request.GET.get('fee_type_id')
    academic_year_id = request.GET.get('academic_year_id')
    period = request.GET.get('period')

    try:
        schedule = PaymentSchedule.objects.get(
            fee_structure__class_level_id=class_id,
            fee_structure__fee_type_id=fee_type_id,
            fee_structure__academic_year_id=academic_year_id,
            fee_structure__is_active=True,
            period=period,
        )
        return JsonResponse({
            'success': True,
            'amount': float(schedule.expected_amount),
            'due_date': schedule.due_date.strftime('%Y-%m-%d'),
        })
    except PaymentSchedule.DoesNotExist:
        # Fallback: return the FeeStructure total amount
        try:
            fs = FeeStructure.objects.get(
                class_level_id=class_id,
                fee_type_id=fee_type_id,
                academic_year_id=academic_year_id,
                is_active=True,
            )
            return JsonResponse({'success': True, 'amount': float(fs.amount), 'due_date': None})
        except FeeStructure.DoesNotExist:
            return JsonResponse({'success': False, 'amount': 0})


@login_required
def get_fee_structures(request):
    """Retourne les types de frais actifs pour une classe (AJAX)"""
    class_id = request.GET.get('class_id')
    academic_year_id = request.GET.get('academic_year_id')

    structures = FeeStructure.objects.filter(
        class_level_id=class_id,
        academic_year_id=academic_year_id,
        is_active=True,
        fee_type__is_active=True,
    ).select_related('fee_type').order_by('fee_type__category', 'fee_type__name')

    data = [{
        'id': fs.fee_type.id,
        'name': fs.fee_type.name,
        'category': fs.fee_type.category,
        'amount': float(fs.amount),
        'frequency': fs.payment_frequency,
    } for fs in structures]

    return JsonResponse({'success': True, 'fee_types': data})


# ===================================
# REPORTS VIEWS
# ===================================

@login_required
def finance_reports(request):
    active_year = AcademicYear.objects.filter(is_active=True).first()
    year_id = request.GET.get('year', '')

    payments = Payment.objects.all()
    if year_id:
        payments = payments.filter(academic_year_id=year_id)
    elif active_year:
        payments = payments.filter(academic_year=active_year)

    stats = payments.aggregate(
        total_received=Sum('paid_amount'),
        total_due=Sum('total_amount'),
    )
    total_received = stats['total_received'] or Decimal('0')
    total_due = stats['total_due'] or Decimal('0')
    total_remaining = total_due - total_received

    by_fee_type = payments.values(
        'fee_type__name', 'fee_type__category'
    ).annotate(
        total=Sum('total_amount'),
        paid=Sum('paid_amount'),
    ).order_by('-paid')

    by_period = payments.exclude(period='').values('period').annotate(
        total=Sum('total_amount'),
        paid=Sum('paid_amount'),
    ).order_by('period')

    today = timezone.now().date()
    month_data = []
    for i in range(6):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        monthly = payments.filter(
            payment_date__year=year,
            payment_date__month=month
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        month_data.append({
            'month': datetime.date(year, month, 1).strftime('%b %Y'),
            'amount': float(monthly),
        })
    month_data.reverse()

    context = {
        'active_year': active_year,
        'academic_years': AcademicYear.objects.all(),
        'selected_year': year_id,
        'total_received': total_received,
        'total_due': total_due,
        'total_remaining': total_remaining,
        'by_fee_type': by_fee_type,
        'by_period': by_period,
        'month_data': month_data,
    }
    return render(request, 'finance/reports.html', context)


# ===================================
# STUDENT ACCOUNT VIEW
# ===================================

@login_required
def student_account(request, student_id):
    """Tableau de bord financier d'un élève"""
    student = get_object_or_404(Student, pk=student_id)
    active_year = AcademicYear.objects.filter(is_active=True).first()
    year_id = request.GET.get('year', '')

    selected_year = None
    if year_id:
        selected_year = AcademicYear.objects.filter(pk=year_id).first()
    elif active_year:
        selected_year = active_year

    payments = Payment.objects.filter(student=student)
    if selected_year:
        payments = payments.filter(academic_year=selected_year)
    payments = payments.select_related('fee_type', 'payment_method').order_by('-payment_date')

    classe = student.class_set.first()
    period_statuses = []
    if selected_year and classe:
        periods = ['trimestre1', 'trimestre2', 'trimestre3']
        period_labels = {
            'trimestre1': 'Trimestre 1',
            'trimestre2': 'Trimestre 2',
            'trimestre3': 'Trimestre 3',
            'semestre1': 'Semestre 1',
            'semestre2': 'Semestre 2',
        }
        for p in periods:
            schedule = PaymentSchedule.objects.filter(
                fee_structure__academic_year=selected_year,
                fee_structure__class_level=classe,
                fee_structure__fee_type__category='scolarite',
                fee_structure__is_active=True,
                period=p,
            ).first()
            if schedule:
                paid = payments.filter(
                    period=p,
                    fee_type__category='scolarite',
                    status__in=['partial', 'completed']
                ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')
                expected = schedule.expected_amount
                period_statuses.append({
                    'period': p,
                    'label': period_labels[p],
                    'expected': expected,
                    'paid': paid,
                    'remaining': max(Decimal('0'), expected - paid),
                    'is_up_to_date': paid >= expected,
                    'due_date': schedule.due_date,
                    'percentage': int(min(100, (paid / expected * 100))) if expected > 0 else 0,
                })

    context = {
        'student': student,
        'classe': classe,
        'payments': payments,
        'academic_years': AcademicYear.objects.all(),
        'selected_year': selected_year,
        'period_statuses': period_statuses,
    }
    return render(request, 'finance/student_account.html', context)


# ===================================
# INTERNAL HELPERS
# ===================================

def _update_student_account(student, academic_year):
    account, _ = StudentAccount.objects.get_or_create(
        student=student,
        academic_year=academic_year,
    )
    account.update_totals()
