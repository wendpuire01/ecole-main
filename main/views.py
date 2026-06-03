from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from decimal import Decimal
import datetime
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Anonce, Notification
from school_portal.models import Student, Class, Teacher, Subject, Mark
from school_finance.models import Payment, Receipt, AcademicYear


def home(request):
    """Page d'accueil - redirige vers dashboard si connecté, sinon vers login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès')
    return redirect('login')


@login_required
def dashboard(request):
    today = timezone.now().date()
    active_year = AcademicYear.objects.filter(is_active=True).first()

    # --- Compteurs généraux ---
    total_students = Student.objects.count()
    total_classes = Class.objects.count()
    total_teachers = Teacher.objects.count()

    # Nouveaux élèves ce mois
    month_start = today.replace(day=1)
    new_students_month = Student.objects.filter(
        created_at__date__gte=month_start
    ).count() if hasattr(Student, 'created_at') else 0

    # --- Statistiques financières (année active) ---
    payments_qs = Payment.objects.all()
    if active_year:
        payments_qs = payments_qs.filter(academic_year=active_year)

    finance_stats = payments_qs.aggregate(
        total_received=Sum('paid_amount'),
        total_due=Sum('total_amount'),
    )
    total_received = finance_stats['total_received'] or Decimal('0')
    total_due = finance_stats['total_due'] or Decimal('0')
    total_remaining = total_due - total_received

    pending_count = payments_qs.filter(status__in=['pending', 'partial']).count()

    # Encaissements du mois en cours
    monthly_received = payments_qs.filter(
        payment_date__gte=month_start
    ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')

    # --- Paiements récents ---
    recent_payments = (
        Payment.objects
        .select_related('student', 'fee_type', 'payment_method')
        .order_by('-payment_date', '-created_at')[:8]
    )

    # --- Activités récentes (reçus + inscriptions) ---
    recent_receipts = (
        Receipt.objects
        .select_related('payment__student', 'payment__fee_type')
        .order_by('-created_at')[:5]
    )

    # --- Évolution mensuelle (6 derniers mois) ---
    month_labels = []
    month_amounts = []
    for i in range(5, -1, -1):
        d = today - datetime.timedelta(days=i * 30)
        label = d.strftime('%b %Y')
        amount = float(
            Payment.objects.filter(
                payment_date__year=d.year,
                payment_date__month=d.month,
            ).aggregate(t=Sum('paid_amount'))['t'] or 0
        )
        month_labels.append(label)
        month_amounts.append(amount)

    # --- Classes avec stats ---
    classes = []
    for cls in Class.objects.prefetch_related('students', 'subject_set').order_by('name')[:6]:
        students_count = cls.students.count()
        subjects_count = cls.subject_set.count()
        classes.append({
            'id': cls.id,
            'name': cls.name,
            'teacher': cls.teacher.name if hasattr(cls, 'teacher') and cls.teacher else '—',
            'students_count': students_count,
            'subjects_count': subjects_count,
        })

    # --- Annonces ---
    announcements = Anonce.objects.order_by('-create_at')[:5]

    context = {
        # Compteurs
        'total_students': total_students,
        'total_classes': total_classes,
        'total_teachers': total_teachers,
        'new_students_month': new_students_month,
        # Finance
        'total_received': total_received,
        'total_due': total_due,
        'total_remaining': total_remaining,
        'pending_count': pending_count,
        'monthly_received': monthly_received,
        'active_year': active_year,
        # Listes
        'recent_payments': recent_payments,
        'recent_receipts': recent_receipts,
        'classes': classes,
        'announcements': announcements,
        # Chart
        'chart_labels': json.dumps(month_labels),
        'chart_amounts': json.dumps(month_amounts),
    }

    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    """Profil utilisateur"""
    context = {
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def settings_view(request):
    """Paramètres de l'application"""
    from school_portal.models import SchoolSettings

    # Récupérer ou créer les paramètres
    school_settings, created = SchoolSettings.objects.get_or_create(
        defaults={
            'name': 'ÉCOLE SECONDAIRE',
            'address': 'Ouagadougou, Burkina Faso',
            'phone': '+226 XX XX XX XX'
        }
    )

    if request.method == 'POST':
        try:
            # Mettre à jour les paramètres
            school_settings.name = request.POST.get('name')
            school_settings.address = request.POST.get('address')
            school_settings.phone = request.POST.get('phone')
            school_settings.email = request.POST.get('email', '')
            school_settings.website = request.POST.get('website', '')
            school_settings.director_name = request.POST.get('director_name', '')
            school_settings.motto = request.POST.get('motto', '')

            # Gérer l'upload du logo
            if 'logo' in request.FILES:
                school_settings.logo = request.FILES['logo']

            school_settings.save()
            messages.success(request, 'Paramètres mis à jour avec succès')
            return redirect('settings')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    context = {
        'school_settings': school_settings,
    }
    return render(request, 'settings.html', context)


# ===================================
# NOTIFICATIONS
# ===================================

@login_required
def notifications_api(request):
    """Retourne les notifications non lues (JSON) pour le polling AJAX."""
    notifs = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).values('id', 'notif_type', 'title', 'body', 'link', 'created_at')[:20]

    data = []
    for n in notifs:
        n['created_at'] = n['created_at'].strftime('%d/%m/%Y %H:%M')
        data.append(n)

    return JsonResponse({
        'count': len(data),
        'notifications': data,
    })


@login_required
@require_POST
def notification_mark_read(request, pk):
    Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
    return JsonResponse({'ok': True})


@login_required
@require_POST
def notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})
