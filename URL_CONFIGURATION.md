# Configuration des URLs - Système de Gestion d'École

## Vue d'Ensemble

Ce document décrit comment configurer les URLs pour faire fonctionner tous les templates créés.

## Structure des URLs

### 1. URLs Principales (school_manager/urls.py)

Créez ou modifiez le fichier `school_manager/urls.py` :

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('portal/', include('school_portal.urls')),
    path('finance/', include('school_finance.urls')),
]

# Servir les fichiers media et static en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 2. URLs Main App (main/urls.py)

Créez `main/urls.py` :

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
]
```

### 3. URLs School Portal (school_portal/urls.py)

Créez `school_portal/urls.py` :

```python
from django.urls import path
from . import views

urlpatterns = [
    # Students
    path('students/', views.students_list, name='students_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/details/', views.student_details, name='student_details'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    # Classes
    path('classes/', views.classes_list, name='classes_list'),
    path('classes/create/', views.class_create, name='classes_create'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    path('classes/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:pk>/students/', views.class_students, name='class_students'),
    path('classes/<int:pk>/grades/', views.class_grades, name='class_grades'),

    # Teachers
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),

    # Subjects
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),

    # Grades
    path('grades/', views.grades_list, name='grades_list'),
    path('grades/save/', views.save_grade, name='save_grade'),
    path('grades/calculate-averages/', views.calculate_averages, name='calculate_averages'),
    path('grades/generate-bulletins/', views.generate_bulletins, name='generate_bulletins'),

    # Reports
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:student_id>/', views.report_card, name='report_card'),
]
```

### 4. URLs Finance (school_finance/urls.py)

Créez `school_finance/urls.py` :

```python
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
```

## Création des Views de Base

### 1. Views Dashboard (main/views.py)

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

@login_required
def dashboard(request):
    context = {
        'total_students': 1234,
        'total_payments': '850K',
        'pending_payments': 156,
        'total_classes': 45,
        'recent_payments': [],
        'classes': [],
    }
    return render(request, 'dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Identifiants incorrects')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def settings(request):
    return render(request, 'settings.html')
```

### 2. Views Classes (school_portal/views.py)

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Class, Student, Teacher, Subject, Mark

@login_required
def classes_list(request):
    classes = Class.objects.all()
    teachers = Teacher.objects.all()
    subjects = Subject.objects.all()

    context = {
        'classes': classes,
        'teachers': teachers,
        'subjects': subjects,
        'total_classes': classes.count(),
        'total_students': Student.objects.count(),
        'total_teachers': teachers.count(),
    }
    return render(request, 'classes/classes_list.html', context)

@login_required
def class_detail(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    return render(request, 'classes/class_detail.html', {'class': class_obj})

@login_required
def class_create(request):
    if request.method == 'POST':
        # Logique de création
        messages.success(request, 'Classe créée avec succès')
        return redirect('classes_list')
    return render(request, 'classes/class_form.html')

@login_required
def class_students(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    students = class_obj.students.all()
    return render(request, 'classes/class_students.html', {
        'class': class_obj,
        'students': students
    })
```

### 3. Views Grades (school_portal/views.py - ajouter)

```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@login_required
def grades_list(request):
    classes = Class.objects.all()
    subjects = Subject.objects.all()

    selected_class = request.GET.get('class')
    students = []

    if selected_class:
        class_obj = get_object_or_404(Class, pk=selected_class)
        students = class_obj.students.all()

    context = {
        'classes': classes,
        'subjects': subjects,
        'students': students,
        'selected_class': selected_class,
    }
    return render(request, 'grades/grades_list.html', context)

@login_required
@require_POST
def save_grade(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student')
        subject_id = data.get('subject')
        score = data.get('score')

        # Sauvegarder la note
        # Mark.objects.update_or_create(...)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def report_card(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    grades = Mark.objects.filter(student=student)

    context = {
        'student': student,
        'grades': grades,
        'school_name': 'ÉCOLE SECONDAIRE',
        'academic_year': '2024-2025',
        'period': 'Trimestre 1',
    }
    return render(request, 'grades/report_card.html', context)
```

### 4. Views Finance (school_finance/views.py)

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def payments_list(request):
    context = {
        'payments': [],
        'classes': [],
        'students': [],
        'total_received': '8.5M',
        'total_pending': '2.3M',
        'total_unpaid': '1.2M',
        'monthly_total': '1.8M',
    }
    return render(request, 'finance/payments_list.html', context)

@login_required
def payment_create(request):
    if request.method == 'POST':
        # Logique de création de paiement
        messages.success(request, 'Paiement enregistré avec succès')
        return redirect('payments_list')
    return render(request, 'finance/payment_form.html')

@login_required
def enrollments_list(request):
    return render(request, 'finance/enrollments_list.html')

@login_required
def finance_reports(request):
    return render(request, 'finance/reports.html')
```

## Templates Additionnels Requis

### 1. Login Template (templates/login.html)

```html
{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - Gestion d'École</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center align-items-center min-vh-100">
            <div class="col-md-5">
                <div class="card shadow-lg border-0">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <div class="school-logo mx-auto mb-3">
                                <i class="fas fa-graduation-cap"></i>
                            </div>
                            <h3>École Manager</h3>
                            <p class="text-muted">Connectez-vous à votre compte</p>
                        </div>

                        {% if messages %}
                            {% for message in messages %}
                            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}

                        <form method="POST">
                            {% csrf_token %}
                            <div class="mb-3">
                                <label class="form-label">Nom d'utilisateur</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-4">
                                <label class="form-label">Mot de passe</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Se connecter</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

## Commandes d'Installation Rapide

```bash
# 1. Activer l'environnement virtuel
venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer les migrations
python manage.py makemigrations

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un superuser
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

## Accès Initial

1. Créez un superuser avec `python manage.py createsuperuser`
2. Connectez-vous sur http://127.0.0.1:8000/admin
3. Créez quelques données de test (enseignants, matières, classes)
4. Accédez au dashboard sur http://127.0.0.1:8000

## Notes Importantes

- Tous les templates utilisent Bootstrap 5 et FontAwesome 6
- Le design est responsive et fonctionne sur mobile
- Les couleurs sont configurables dans `static/css/main.css`
- Les bulletins sont prêts à imprimer avec un style professionnel
- Le système supporte l'export Excel et PDF

---

**Pour toute question, consultez INSTALLATION.md ou la documentation Django**
