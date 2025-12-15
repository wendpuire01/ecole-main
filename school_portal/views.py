from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count, Q
from datetime import datetime
import json

from .models import Student, Class, Teacher, Subject, Mark, Assignment


# ===================================
# STUDENTS VIEWS
# ===================================

@login_required
def students_list(request):
    """Liste de tous les étudiants"""
    students = Student.objects.all().order_by('name')

    # Filtres
    search = request.GET.get('search', '')
    class_filter = request.GET.get('class', '')

    if search:
        students = students.filter(
            Q(name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(surname__icontains=search)
        )

    if class_filter:
        students = students.filter(id=class_filter)  # À adapter selon votre modèle

    classes = Class.objects.all()

    context = {
        'students': students,
        'classes': classes,
        'total_students': Student.objects.count(),
    }
    return render(request, 'students/students_list.html', context)


@login_required
def student_detail(request, pk):
    """Détails d'un étudiant"""
    student = get_object_or_404(Student, pk=pk)
    marks = Mark.objects.filter(student=student).select_related('assignment__subject')

    context = {
        'student': student,
        'marks': marks,
    }
    return render(request, 'students/student_detail.html', context)


@login_required
def student_create(request):
    """Créer un nouvel étudiant"""
    if request.method == 'POST':
        try:
            student = Student.objects.create(
                name=request.POST.get('name'),
                first_name=request.POST.get('first_name'),
                surname=request.POST.get('surname', ''),
                birth_date=request.POST.get('birth_date'),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
            )
            messages.success(request, f'Étudiant {student.name} créé avec succès')
            return redirect('students_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    classes = Class.objects.all()
    context = {'classes': classes}
    return render(request, 'students/student_form.html', context)


@login_required
def student_edit(request, pk):
    """Modifier un étudiant"""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        try:
            student.name = request.POST.get('name')
            student.first_name = request.POST.get('first_name')
            student.surname = request.POST.get('surname', '')
            student.birth_date = request.POST.get('birth_date')
            student.email = request.POST.get('email', '')
            student.phone = request.POST.get('phone')
            student.address = request.POST.get('address')
            student.save()
            messages.success(request, 'Étudiant modifié avec succès')
            return redirect('student_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    context = {'student': student}
    return render(request, 'students/student_form.html', context)


@login_required
def student_delete(request, pk):
    """Supprimer un étudiant"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Étudiant supprimé avec succès')
        return redirect('students_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


# ===================================
# CLASSES VIEWS
# ===================================

@login_required
def classes_list(request):
    """Liste de toutes les classes"""

    # Gérer la création depuis la modale
    if request.method == 'POST':
        print("=== DEBUT CREATION CLASSE (depuis modale) ===")
        print("POST data:", request.POST)

        try:
            name = request.POST.get('name')
            level = request.POST.get('level')
            teacher_id = request.POST.get('teacher')

            print(f"Nom: {name}")
            print(f"Niveau: {level}")
            print(f"Teacher ID: {teacher_id}")

            # Vérifier que les champs obligatoires sont remplis
            if not name or not level:
                messages.error(request, 'Le nom et le niveau sont obligatoires')
            else:
                class_obj = Class.objects.create(
                    name=name,
                    level=level,
                    teacher_id=teacher_id if teacher_id else None,
                )

                print(f"Classe créée: {class_obj.id} - {class_obj.name}")

                # Ajouter les matières
                subjects_ids = request.POST.getlist('subjects')
                print(f"Matières sélectionnées: {subjects_ids}")

                for subject_id in subjects_ids:
                    subject = Subject.objects.get(pk=subject_id)
                    subject.classes.add(class_obj)
                    print(f"Matière ajoutée: {subject.name}")

                messages.success(request, f'Classe {class_obj.name} créée avec succès')
                print("=== FIN CREATION CLASSE - SUCCESS ===")
                return redirect('classes_list')
        except Exception as e:
            print(f"=== ERREUR: {str(e)} ===")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    classes_query = Class.objects.all().select_related('teacher')

    # Enrichir avec les statistiques
    classes = []
    for class_obj in classes_query:
        students_count = class_obj.students.count()
        subjects_count = class_obj.subject_set.count()

        # Calculer la moyenne de la classe
        class_average = Mark.objects.filter(
            student__in=class_obj.students.all()
        ).aggregate(avg=Avg('score'))['avg']

        # Matières principales (3 premières)
        main_subjects = class_obj.subject_set.all()[:3]

        classes.append({
            'id': class_obj.id,
            'name': class_obj.name,
            'level': class_obj.level,
            'teacher': class_obj.teacher,
            'students_count': students_count,
            'subjects_count': subjects_count,
            'average': round(class_average, 2) if class_average else None,
            'main_subjects': [{'short_name': s.name[:4].upper()} for s in main_subjects],
        })

    teachers = Teacher.objects.all()
    subjects = Subject.objects.all()

    context = {
        'classes': classes,
        'teachers': teachers,
        'subjects': subjects,
        'total_classes': len(classes),
        'total_students': Student.objects.count(),
        'total_teachers': teachers.count(),
    }
    return render(request, 'classes/classes_list.html', context)


@login_required
def class_create(request):
    """Créer une nouvelle classe"""
    if request.method == 'POST':
        print("=== DEBUT CREATION CLASSE ===")
        print("POST data:", request.POST)

        try:
            name = request.POST.get('name')
            level = request.POST.get('level')
            teacher_id = request.POST.get('teacher')

            print(f"Nom: {name}")
            print(f"Niveau: {level}")
            print(f"Teacher ID: {teacher_id}")

            # Vérifier que les champs obligatoires sont remplis
            if not name or not level:
                messages.error(request, 'Le nom et le niveau sont obligatoires')
                teachers = Teacher.objects.all()
                subjects = Subject.objects.all()
                context = {'teachers': teachers, 'subjects': subjects}
                return render(request, 'classes/class_form.html', context)

            class_obj = Class.objects.create(
                name=name,
                level=level,
                teacher_id=teacher_id if teacher_id else None,
            )

            print(f"Classe créée: {class_obj.id} - {class_obj.name}")

            # Ajouter les matières
            subjects = request.POST.getlist('subjects')
            print(f"Matières sélectionnées: {subjects}")

            for subject_id in subjects:
                subject = Subject.objects.get(pk=subject_id)
                subject.classes.add(class_obj)
                print(f"Matière ajoutée: {subject.name}")

            messages.success(request, f'Classe {class_obj.name} créée avec succès')
            print("=== FIN CREATION CLASSE - SUCCESS ===")
            return redirect('classes_list')
        except Exception as e:
            print(f"=== ERREUR: {str(e)} ===")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    teachers = Teacher.objects.all()
    subjects = Subject.objects.all()
    context = {'teachers': teachers, 'subjects': subjects}
    return render(request, 'classes/class_form.html', context)


@login_required
def class_detail(request, pk):
    """Détails d'une classe"""
    class_obj = get_object_or_404(Class, pk=pk)
    students = class_obj.students.all()
    subjects = class_obj.subject_set.all()

    context = {
        'class': class_obj,
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'classes/class_detail.html', context)


@login_required
def assign_students(request, pk):
    """Assigner des étudiants à une classe"""
    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        print(f"=== ASSIGNATION ETUDIANTS ===")
        print(f"Classe: {class_obj.name}")
        print(f"Etudiants sélectionnés: {student_ids}")

        # Vider les étudiants actuels et ajouter les nouveaux
        class_obj.students.clear()
        for student_id in student_ids:
            student = Student.objects.get(pk=student_id)
            class_obj.students.add(student)
            print(f"Etudiant ajouté: {student.name} {student.first_name}")

        messages.success(request, f'{len(student_ids)} étudiant(s) assigné(s) à {class_obj.name}')
        return redirect('class_detail', pk=pk)

    all_students = Student.objects.all()
    assigned_students = [s.id for s in class_obj.students.all()]

    context = {
        'class': class_obj,
        'all_students': all_students,
        'assigned_students': assigned_students,
    }
    return render(request, 'classes/assign_students.html', context)


@login_required
def class_edit(request, pk):
    """Modifier une classe"""
    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        try:
            class_obj.name = request.POST.get('name')
            class_obj.level = request.POST.get('level')
            if request.POST.get('teacher'):
                class_obj.teacher_id = request.POST.get('teacher')
            class_obj.save()
            messages.success(request, 'Classe modifiée avec succès')
            return redirect('class_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    teachers = Teacher.objects.all()
    context = {'class': class_obj, 'teachers': teachers}
    return render(request, 'classes/class_form.html', context)


@login_required
def class_students(request, pk):
    """Liste des étudiants d'une classe"""
    class_obj = get_object_or_404(Class, pk=pk)
    students = class_obj.students.all()

    context = {
        'class': class_obj,
        'students': students,
    }
    return render(request, 'classes/class_students.html', context)


@login_required
def class_grades(request, pk):
    """Notes d'une classe"""
    return redirect(f'/portal/grades/?class={pk}')


# ===================================
# TEACHERS VIEWS
# ===================================

@login_required
def teachers_list(request):
    """Liste de tous les enseignants"""
    teachers = Teacher.objects.all().annotate(
        classes_count=Count('class'),
        subjects_count=Count('subject')
    )

    context = {
        'teachers': teachers,
        'total_teachers': teachers.count(),
    }
    return render(request, 'teachers/teachers_list.html', context)


@login_required
def teacher_create(request):
    """Créer un nouvel enseignant"""
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.create(
                name=request.POST.get('name'),
                first_name=request.POST.get('first_name'),
                surname=request.POST.get('surname', ''),
                birth_date=request.POST.get('birth_date'),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
            )
            messages.success(request, f'Enseignant {teacher.name} créé avec succès')
            return redirect('teachers_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    return render(request, 'teachers/teacher_form.html')


@login_required
def teacher_detail(request, pk):
    """Détails d'un enseignant"""
    teacher = get_object_or_404(Teacher, pk=pk)
    classes = Class.objects.filter(teacher=teacher)
    subjects = Subject.objects.filter(teacher=teacher)

    context = {
        'teacher': teacher,
        'classes': classes,
        'subjects': subjects,
    }
    return render(request, 'teachers/teacher_detail.html', context)


# ===================================
# SUBJECTS VIEWS
# ===================================

@login_required
def subjects_list(request):
    """Liste de toutes les matières"""
    subjects = Subject.objects.all().select_related('teacher')

    context = {
        'subjects': subjects,
        'total_subjects': subjects.count(),
    }
    return render(request, 'subjects/subjects_list.html', context)


@login_required
def subject_create(request):
    """Créer une nouvelle matière"""
    if request.method == 'POST':
        try:
            subject = Subject.objects.create(
                name=request.POST.get('name'),
                teacher_id=request.POST.get('teacher') if request.POST.get('teacher') else None,
            )
            messages.success(request, f'Matière {subject.name} créée avec succès')
            return redirect('subjects_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    teachers = Teacher.objects.all()
    context = {'teachers': teachers}
    return render(request, 'subjects/subject_form.html', context)


# ===================================
# GRADES VIEWS
# ===================================

@login_required
def grades_list(request):
    """Gestion des notes"""

    # Gérer l'ajout de note depuis la modale
    if request.method == 'POST':
        print("=== DEBUT AJOUT NOTE ===")
        print("POST data:", request.POST)

        try:
            student_id = request.POST.get('student')
            subject_id = request.POST.get('subject')
            score = float(request.POST.get('score'))
            evaluation_type = request.POST.get('evaluation_type', 'devoir')
            coefficient = int(request.POST.get('coefficient', 1))
            date_str = request.POST.get('date')
            observations = request.POST.get('observations', '')

            print(f"Student: {student_id}, Subject: {subject_id}, Score: {score}")

            student = Student.objects.get(pk=student_id)
            subject = Subject.objects.get(pk=subject_id)

            # Créer un assignment
            from datetime import datetime
            assignment = Assignment.objects.create(
                name=f'{subject.name} - {evaluation_type}',
                description=observations,
                subject=subject,
                due_date=datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date(),
                points=20
            )

            # Créer la note
            mark = Mark.objects.create(
                student=student,
                assignment=assignment,
                score=score,
                date=datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
            )

            print(f"Note créée: {mark.id}")
            messages.success(request, f'Note de {score}/20 ajoutée pour {student.name} {student.first_name}')
            print("=== FIN AJOUT NOTE - SUCCESS ===")
            return redirect('grades_list')

        except Exception as e:
            print(f"=== ERREUR: {str(e)} ===")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur lors de l\'ajout de la note: {str(e)}')

    classes = Class.objects.all()
    subjects = Subject.objects.all()

    selected_class = request.GET.get('class')
    selected_subject = request.GET.get('subject')

    students = []
    subjects_list = []

    if selected_class:
        class_obj = get_object_or_404(Class, pk=selected_class)
        students_query = class_obj.students.all()
        subjects_list_raw = class_obj.subject_set.all()

        # Ajouter short_name aux matières
        subjects_list = []
        for subject in subjects_list_raw:
            subjects_list.append({
                'id': subject.id,
                'name': subject.name,
                'short_name': subject.name[:4].upper() if len(subject.name) > 4 else subject.name.upper(),
            })

        # Préparer les données pour le tableau
        for student in students_query:
            grades = []
            total_points = 0
            total_coefficients = 0

            for subject_data in subjects_list:
                # Récupérer la note pour cette matière
                mark = Mark.objects.filter(
                    student=student,
                    assignment__subject_id=subject_data['id']
                ).first()

                grade_data = {
                    'subject_id': subject_data['id'],
                    'score': mark.score if mark else None
                }
                grades.append(grade_data)

                if mark:
                    coefficient = 1  # À remplacer par le vrai coefficient
                    total_points += mark.score * coefficient
                    total_coefficients += coefficient

            # Calculer la moyenne
            average = round(total_points / total_coefficients, 2) if total_coefficients > 0 else None

            students.append({
                'id': student.id,
                'name': f'{student.name} {student.first_name}',
                'matricule': f'ET-{student.id:04d}',
                'class': class_obj.name,
                'grades': grades,
                'average': average,
                'rank': None,  # À calculer
            })

        # Calculer les rangs
        students_sorted = sorted([s for s in students if s['average']],
                                key=lambda x: x['average'], reverse=True)
        for rank, student in enumerate(students_sorted, 1):
            for s in students:
                if s['id'] == student['id']:
                    s['rank'] = rank

    # Statistiques
    class_average = None
    if students and any(s['average'] for s in students):
        averages = [s['average'] for s in students if s['average']]
        class_average = round(sum(averages) / len(averages), 2) if averages else None

    context = {
        'classes': classes,
        'subjects': subjects,
        'students': students,
        'subjects_list': subjects_list,
        'selected_class': int(selected_class) if selected_class else None,
        'selected_subject': int(selected_subject) if selected_subject else None,
        'class_average': class_average,
        'highest_grade': max([s['average'] for s in students if s['average']], default=None),
        'total_grades': Mark.objects.count(),
        'all_students': Student.objects.all(),
        'all_subjects': subjects,
    }
    return render(request, 'grades/grades_list.html', context)


@login_required
@require_POST
def save_grade(request):
    """Sauvegarder une note (AJAX)"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student')
        subject_id = data.get('subject')
        score = float(data.get('score', 0))

        student = Student.objects.get(pk=student_id)
        subject = Subject.objects.get(pk=subject_id)

        # Créer ou récupérer un assignment par défaut
        assignment, created = Assignment.objects.get_or_create(
            name=f'{subject.name} - Évaluation',
            subject=subject,
            defaults={
                'description': 'Évaluation générale',
                'due_date': datetime.now().date(),
                'points': 20
            }
        )

        # Créer ou mettre à jour la note
        mark, created = Mark.objects.update_or_create(
            student=student,
            assignment=assignment,
            defaults={
                'score': score,
                'date': datetime.now().date()
            }
        )

        return JsonResponse({'success': True, 'message': 'Note enregistrée'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def calculate_averages(request):
    """Calculer les moyennes (AJAX)"""
    try:
        # Logique de calcul des moyennes
        # Déjà calculé dans grades_list
        return JsonResponse({'success': True, 'message': 'Moyennes calculées'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def generate_bulletins(request):
    """Générer les bulletins pour une classe"""
    class_id = request.GET.get('class')
    if class_id:
        class_obj = get_object_or_404(Class, pk=class_id)
        students = class_obj.students.all()
        # Rediriger vers le premier bulletin
        if students.exists():
            return redirect('report_card', student_id=students.first().id)

    messages.warning(request, 'Veuillez sélectionner une classe')
    return redirect('grades_list')


# ===================================
# REPORTS VIEWS
# ===================================

@login_required
def reports_list(request):
    """Liste des bulletins"""
    students = Student.objects.all()

    context = {
        'students': students,
    }
    return render(request, 'grades/reports_list.html', context)


@login_required
def report_card(request, student_id):
    """Bulletin de notes d'un étudiant"""
    student = get_object_or_404(Student, pk=student_id)

    # Récupérer toutes les notes de l'étudiant
    marks = Mark.objects.filter(student=student).select_related(
        'assignment__subject', 'assignment__subject__teacher'
    )

    # Organiser les notes par matière
    grades = []
    total_points = 0
    total_coefficients = 0

    subjects_dict = {}
    for mark in marks:
        subject = mark.assignment.subject
        if subject.name not in subjects_dict:
            subjects_dict[subject.name] = {
                'subject': subject.name,
                'teacher': subject.teacher.name if subject.teacher else 'N/A',
                'coefficient': 1,  # À adapter
                'score': mark.score,
                'total': mark.score * 1,
                'rank': None,
            }

    grades = list(subjects_dict.values())

    # Calculer les totaux
    for grade in grades:
        total_points += grade['total']
        total_coefficients += grade['coefficient']

    average = round(total_points / total_coefficients, 2) if total_coefficients > 0 else 0

    # Appréciation
    if average >= 16:
        appreciation = "Excellent élève. Travail remarquable. Continuez ainsi!"
    elif average >= 14:
        appreciation = "Très bon élève. Résultats très satisfaisants. Poursuivez vos efforts."
    elif average >= 12:
        appreciation = "Bon élève. Travail sérieux. Peut mieux faire."
    elif average >= 10:
        appreciation = "Travail satisfaisant. Efforts à poursuivre."
    else:
        appreciation = "Résultats insuffisants. Travail et concentration nécessaires."

    context = {
        'student': {
            'full_name': f'{student.name} {student.first_name} {student.surname}',
            'matricule': f'ET-{student.id:04d}',
            'class': 'Terminale S1',  # À adapter
            'birth_date': student.birth_date,
        },
        'grades': grades,
        'total_points': total_points,
        'total_coefficients': total_coefficients,
        'average': average,
        'rank': None,  # À calculer
        'class_size': 45,  # À adapter
        'appreciation': appreciation,
        'school_name': 'ÉCOLE SECONDAIRE',
        'school_address': 'Ouagadougou, Burkina Faso',
        'school_phone': '+226 XX XX XX XX',
        'academic_year': '2024-2025',
        'period': 'Trimestre 1',
        'class_teacher': 'M. OUEDRAOGO',
        'total_days': 60,
        'absences': 2,
        'tardies': 1,
        'current_date': datetime.now(),
    }

    return render(request, 'grades/report_card.html', context)
