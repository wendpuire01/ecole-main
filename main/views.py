from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from decimal import Decimal
import datetime
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Anonce, Notification, UserProfile
from .decorators import admin_required, management_required
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
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Ce compte est désactivé.')
                return render(request, 'login.html')

            login(request, user)

            # Session expiry: 30 jours si "remember me", sinon 8 heures
            if remember_me:
                request.session.set_expiry(30 * 24 * 3600)
            else:
                request.session.set_expiry(8 * 3600)

            # Méta-données de session
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR', '')
            request.session['login_ip'] = ip
            request.session['login_ua'] = request.META.get('HTTP_USER_AGENT', '')[:200]
            request.session['login_time'] = timezone.now().isoformat()

            role_label = user.profile.get_role_display() if hasattr(user, 'profile') else 'Utilisateur'
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} ({role_label}) !')
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
    """Profil utilisateur — modification des infos et du mot de passe"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit_profile':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name  = request.POST.get('last_name', '').strip()
            user.email      = request.POST.get('email', '').strip()
            profile.phone   = request.POST.get('phone', '').strip()
            user.save()
            profile.save()
            messages.success(request, 'Profil mis à jour avec succès.')

        elif action == 'change_password':
            current  = request.POST.get('current_password', '')
            new_pwd  = request.POST.get('new_password', '')
            confirm  = request.POST.get('confirm_password', '')

            if not user.check_password(current):
                messages.error(request, 'Mot de passe actuel incorrect.')
            elif len(new_pwd) < 6:
                messages.error(request, 'Le nouveau mot de passe doit contenir au moins 6 caractères.')
            elif new_pwd != confirm:
                messages.error(request, 'Les deux nouveaux mots de passe ne correspondent pas.')
            else:
                user.set_password(new_pwd)
                user.save()
                # Maintenir la session active après changement de mot de passe
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, 'Mot de passe modifié avec succès.')

        return redirect('profile')

    return render(request, 'profile.html', {'user_profile': profile})


@login_required
def settings_view(request):
    from school_portal.models import SchoolSettings
    from school_finance.models import (
        AcademicYear, FeeType, FeeStructure, PaymentMethod, PaymentSchedule
    )
    from school_portal.models import Class

    school_settings, _ = SchoolSettings.objects.get_or_create(
        defaults={
            'name': 'ÉCOLE SECONDAIRE',
            'address': 'Ouagadougou, Burkina Faso',
            'phone': '+226 XX XX XX XX',
        }
    )

    if request.method == 'POST':
        try:
            school_settings.name = request.POST.get('name')
            school_settings.address = request.POST.get('address')
            school_settings.phone = request.POST.get('phone')
            school_settings.email = request.POST.get('email', '')
            school_settings.website = request.POST.get('website', '')
            school_settings.director_name = request.POST.get('director_name', '')
            school_settings.motto = request.POST.get('motto', '')
            if 'logo' in request.FILES:
                school_settings.logo = request.FILES['logo']
            school_settings.save()
            messages.success(request, 'Paramètres mis à jour avec succès')
            return redirect(request.get_full_path())
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    # Filtre année pour l'onglet frais par classe
    selected_year_id = request.GET.get('year', '')
    active_year = AcademicYear.objects.filter(is_active=True).first()
    filter_year = None
    if selected_year_id:
        filter_year = AcademicYear.objects.filter(pk=selected_year_id).first()
    elif active_year:
        filter_year = active_year

    fee_structures = FeeStructure.objects.select_related(
        'academic_year', 'class_level', 'fee_type'
    ).prefetch_related('schedules').order_by('class_level__name', 'fee_type__category')
    if filter_year:
        fee_structures = fee_structures.filter(academic_year=filter_year)

    context = {
        'school_settings': school_settings,
        'active_tab': request.GET.get('tab', 'ecole'),
        # Finance data
        'academic_years': AcademicYear.objects.all(),
        'fee_types': FeeType.objects.all().order_by('category', 'name'),
        'payment_methods': PaymentMethod.objects.all(),
        'fee_structures': fee_structures,
        'classes': Class.objects.all().order_by('name'),
        'fee_type_categories': FeeType.CATEGORY_CHOICES,
        'filter_year': filter_year,
        'selected_year_id': selected_year_id,
        'period_choices': [
            ('trimestre1', 'Trimestre 1'), ('trimestre2', 'Trimestre 2'),
            ('trimestre3', 'Trimestre 3'), ('semestre1', 'Semestre 1'),
            ('semestre2', 'Semestre 2'),
        ],
    }
    return render(request, 'settings.html', context)


# ===================================
# GESTION DES UTILISATEURS
# ===================================

@login_required
@admin_required
def users_list(request):
    users = User.objects.select_related('profile').order_by('username')
    active_count   = users.filter(is_active=True).count()
    inactive_count = users.filter(is_active=False).count()
    return render(request, 'users/list.html', {
        'users': users,
        'active_count': active_count,
        'inactive_count': inactive_count,
    })


@login_required
@admin_required
def user_create(request):
    teachers = Teacher.objects.all().order_by('name')
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '')
        role       = request.POST.get('role', 'admin')
        teacher_id = request.POST.get('teacher_id') or None
        phone      = request.POST.get('phone', '').strip()

        if not username or not password:
            messages.error(request, 'Le nom d\'utilisateur et le mot de passe sont requis.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.phone = phone
            if teacher_id and role == 'educator':
                profile.teacher_id = teacher_id
            profile.save()
            messages.success(request, f'Utilisateur « {username} » créé avec succès.')
            return redirect('users_list')

    return render(request, 'users/form.html', {
        'action': 'create',
        'role_choices': UserProfile.ROLE_CHOICES,
        'teachers': teachers,
        'target_user': None,
        'profile': None,
    })


@login_required
@admin_required
def user_edit(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    teachers = Teacher.objects.all().order_by('name')

    if request.method == 'POST':
        target_user.first_name = request.POST.get('first_name', '').strip()
        target_user.last_name  = request.POST.get('last_name', '').strip()
        target_user.email      = request.POST.get('email', '').strip()
        target_user.is_active  = bool(request.POST.get('is_active'))
        target_user.save()

        profile.role  = request.POST.get('role', profile.role)
        profile.phone = request.POST.get('phone', '').strip()
        teacher_id    = request.POST.get('teacher_id') or None
        if profile.role == 'educator' and teacher_id:
            profile.teacher_id = teacher_id
        else:
            profile.teacher = None
        profile.save()

        messages.success(request, f'Utilisateur « {target_user.username} » mis à jour.')
        return redirect('users_list')

    return render(request, 'users/form.html', {
        'action': 'edit',
        'target_user': target_user,
        'profile': profile,
        'role_choices': UserProfile.ROLE_CHOICES,
        'teachers': teachers,
    })


@login_required
@admin_required
@require_POST
def user_toggle_active(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status = 'activé' if target_user.is_active else 'désactivé'
        messages.success(request, f'Compte « {target_user.username} » {status}.')
    return redirect('users_list')


@login_required
@admin_required
def user_change_password(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm      = request.POST.get('confirm_password', '')
        if not new_password or len(new_password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
        elif new_password != confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        else:
            target_user.set_password(new_password)
            target_user.save()
            messages.success(request, f'Mot de passe de « {target_user.username} » modifié.')
            return redirect('users_list')
    return render(request, 'users/change_password.html', {'target_user': target_user})


# ===================================
# GESTION DES SESSIONS
# ===================================

@login_required
@admin_required
def sessions_list(request):
    from django.contrib.sessions.models import Session

    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).order_by('-expire_date')
    session_data = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id')
        if not user_id:
            continue
        try:
            s_user = User.objects.select_related('profile').get(pk=user_id)
        except User.DoesNotExist:
            continue

        login_time_str = data.get('login_time', '')
        try:
            import dateutil.parser
            login_time = dateutil.parser.parse(login_time_str) if login_time_str else None
        except Exception:
            login_time = None

        session_data.append({
            'key':         session.session_key,
            'user':        s_user,
            'ip':          data.get('login_ip', '—'),
            'ua':          data.get('login_ua', '—'),
            'login_time':  login_time,
            'expire_date': session.expire_date,
            'is_current':  session.session_key == request.session.session_key,
        })

    return render(request, 'sessions/list.html', {'sessions': session_data})


@login_required
@admin_required
@require_POST
def session_delete(request, session_key):
    from django.contrib.sessions.models import Session
    if session_key == request.session.session_key:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre session.')
    else:
        Session.objects.filter(session_key=session_key).delete()
        messages.success(request, 'Session supprimée — utilisateur déconnecté.')
    return redirect('sessions_list')


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
