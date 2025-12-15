from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from .models import Anonce
from school_portal.models import Student, Class, Teacher, Subject, Mark
from datetime import datetime, timedelta


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
    """Dashboard principal avec statistiques"""

    # Statistiques générales
    total_students = Student.objects.count()
    total_classes = Class.objects.count()
    total_teachers = Teacher.objects.count()

    # Calcul des statistiques financières (simulées pour l'instant)
    # À remplacer par de vraies données quand le module finance sera prêt
    total_payments = 8500000  # FCFA
    pending_payments = 156

    # Paiements récents (simulés)
    recent_payments = [
        {
            'student_name': 'Jean KABORE',
            'student_class': 'Terminale S1',
            'type': 'Scolarité',
            'amount': '150,000',
            'date': datetime.now() - timedelta(minutes=5),
            'status': 'Payé',
            'status_color': 'success'
        },
        {
            'student_name': 'Marie TRAORE',
            'student_class': 'Première L2',
            'type': 'Inscription',
            'amount': '200,000',
            'date': datetime.now() - timedelta(hours=1),
            'status': 'Payé',
            'status_color': 'success'
        },
        {
            'student_name': 'Paul OUEDRAOGO',
            'student_class': 'Seconde A',
            'type': 'Scolarité',
            'amount': '150,000',
            'date': datetime.now() - timedelta(hours=2),
            'status': 'En attente',
            'status_color': 'warning'
        },
    ]

    # Classes avec statistiques
    classes = []
    for class_obj in Class.objects.all()[:6]:
        students_count = class_obj.students.count()
        subjects_count = class_obj.subject_set.count()

        # Calculer la moyenne de la classe (si des notes existent)
        class_average = Mark.objects.filter(
            student__class=class_obj
        ).aggregate(avg=Avg('score'))['avg']

        classes.append({
            'id': class_obj.id,
            'name': class_obj.name,
            'teacher': class_obj.teacher.name if class_obj.teacher else 'Non assigné',
            'students_count': students_count,
            'subjects_count': subjects_count,
            'average': round(class_average, 2) if class_average else None,
        })

    # Annonces récentes
    announcements = Anonce.objects.all().order_by('-create_at')[:5]

    context = {
        'total_students': total_students,
        'total_payments': f'{total_payments/1000000:.1f}M' if total_payments > 1000000 else f'{total_payments/1000:.0f}K',
        'pending_payments': pending_payments,
        'total_classes': total_classes,
        'total_teachers': total_teachers,
        'recent_payments': recent_payments,
        'classes': classes,
        'announcements': announcements,
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
    if request.method == 'POST':
        # Traiter les modifications de paramètres
        messages.success(request, 'Paramètres mis à jour avec succès')
        return redirect('settings')

    context = {}
    return render(request, 'settings.html', context)
