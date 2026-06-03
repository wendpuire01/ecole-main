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
            # Gérer la date de naissance (optionnelle)
            birth_date = request.POST.get('birth_date', '').strip()
            birth_date = birth_date if birth_date else None

            student = Student.objects.create(
                name=request.POST.get('name'),
                first_name=request.POST.get('first_name'),
                surname=request.POST.get('surname', ''),
                birth_date=birth_date,
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
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

            # Gérer la date de naissance (peut être vide)
            birth_date = request.POST.get('birth_date', '').strip()
            if birth_date:
                student.birth_date = birth_date

            student.email = request.POST.get('email', '')
            student.phone = request.POST.get('phone', '')
            student.address = request.POST.get('address', '')
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
    """Créer une nouvelle classe avec matières et enseignants"""
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

            # Créer la classe
            class_obj = Class.objects.create(
                name=name,
                level=level,
                teacher_id=teacher_id if teacher_id else None,
            )

            print(f"Classe créée: {class_obj.id} - {class_obj.name}")

            # Récupérer les matières, enseignants et coefficients
            subject_ids = request.POST.getlist('subjects[]')
            teacher_ids = request.POST.getlist('teachers[]')
            coefficients = request.POST.getlist('coefficients[]')

            print(f"Matières: {subject_ids}")
            print(f"Enseignants: {teacher_ids}")
            print(f"Coefficients: {coefficients}")

            # Importer le modèle SubjectClass
            from .models import SubjectClass

            # Créer les associations matière-classe avec enseignant et coefficient
            for i, subject_id in enumerate(subject_ids):
                if subject_id:  # Si une matière est sélectionnée
                    subject = Subject.objects.get(pk=subject_id)
                    teacher_id_for_subject = teacher_ids[i] if i < len(teacher_ids) else None
                    coefficient = int(coefficients[i]) if i < len(coefficients) and coefficients[i] else 1

                    # Ajouter la classe à la matière
                    subject.classes.add(class_obj)

                    # Créer l'entrée SubjectClass avec l'enseignant et le coefficient
                    SubjectClass.objects.create(
                        subject=subject,
                        classe=class_obj,
                        teacher_id=teacher_id_for_subject if teacher_id_for_subject else None,
                        coefficient=coefficient
                    )

                    teacher_name = Teacher.objects.get(pk=teacher_id_for_subject).name if teacher_id_for_subject else "Non assigné"
                    print(f"Matière ajoutée: {subject.name} - Prof: {teacher_name} - Coef: {coefficient}")

            messages.success(request, f'Classe {class_obj.name} créée avec succès avec {len(subject_ids)} matière(s)')
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
            # Mettre à jour les informations de base
            class_obj.name = request.POST.get('name')
            class_obj.level = request.POST.get('level')
            teacher_id = request.POST.get('teacher')
            class_obj.teacher_id = teacher_id if teacher_id else None
            class_obj.save()

            # Importer le modèle SubjectClass
            from .models import SubjectClass

            # Supprimer les anciennes associations SubjectClass
            SubjectClass.objects.filter(classe=class_obj).delete()

            # Vider les matières associées
            class_obj.subject_set.clear()

            # Récupérer les nouvelles matières, enseignants et coefficients
            subject_ids = request.POST.getlist('subjects[]')
            teacher_ids = request.POST.getlist('teachers[]')
            coefficients = request.POST.getlist('coefficients[]')

            # Créer les nouvelles associations
            for i, subject_id in enumerate(subject_ids):
                if subject_id:
                    subject = Subject.objects.get(pk=subject_id)
                    teacher_id_for_subject = teacher_ids[i] if i < len(teacher_ids) else None
                    coefficient = int(coefficients[i]) if i < len(coefficients) and coefficients[i] else 1

                    # Ajouter la classe à la matière
                    subject.classes.add(class_obj)

                    # Créer l'entrée SubjectClass
                    SubjectClass.objects.create(
                        subject=subject,
                        classe=class_obj,
                        teacher_id=teacher_id_for_subject if teacher_id_for_subject else None,
                        coefficient=coefficient
                    )

            messages.success(request, f'Classe {class_obj.name} modifiée avec succès')
            return redirect('class_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    # Charger les données pour l'affichage
    teachers = Teacher.objects.all()
    subjects = Subject.objects.all()

    # Récupérer les matières actuelles de la classe avec leurs enseignants et coefficients
    from .models import SubjectClass
    subject_classes = SubjectClass.objects.filter(classe=class_obj).select_related('subject', 'teacher')

    context = {
        'class': class_obj,
        'teachers': teachers,
        'subjects': subjects,
        'subject_classes': subject_classes,
        'is_edit': True,
    }
    return render(request, 'classes/class_form.html', context)


@login_required
def class_delete(request, pk):
    """Supprimer une classe"""
    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        class_name = class_obj.name
        class_obj.delete()
        messages.success(request, f'Classe {class_name} supprimée avec succès')
        return redirect('classes_list')

    # Compter les dépendances
    from .models import SubjectClass
    students_count = class_obj.students.count()
    subjects_count = class_obj.subject_set.count()
    subject_classes_count = SubjectClass.objects.filter(classe=class_obj).count()

    context = {
        'class': class_obj,
        'students_count': students_count,
        'subjects_count': subjects_count,
        'subject_classes_count': subject_classes_count,
    }
    return render(request, 'classes/class_confirm_delete.html', context)


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
            # Gérer la date de naissance (optionnelle)
            birth_date = request.POST.get('birth_date', '').strip()
            birth_date = birth_date if birth_date else None

            teacher = Teacher.objects.create(
                name=request.POST.get('name'),
                first_name=request.POST.get('first_name'),
                surname=request.POST.get('surname', ''),
                birth_date=birth_date,
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


@login_required
def teacher_edit(request, pk):
    """Modifier un enseignant"""
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        try:
            teacher.name = request.POST.get('name')
            teacher.first_name = request.POST.get('first_name')
            teacher.surname = request.POST.get('surname', '')

            # Gérer la date de naissance (peut être vide)
            birth_date = request.POST.get('birth_date', '').strip()
            if birth_date:
                teacher.birth_date = birth_date

            teacher.email = request.POST.get('email', '')
            teacher.phone = request.POST.get('phone')
            teacher.address = request.POST.get('address')
            teacher.save()
            messages.success(request, 'Enseignant modifié avec succès')
            return redirect('teacher_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    context = {'teacher': teacher}
    return render(request, 'teachers/teacher_form.html', context)


@login_required
def teacher_delete(request, pk):
    """Supprimer un enseignant"""
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher_name = f"{teacher.name} {teacher.first_name}"
        teacher.delete()
        messages.success(request, f'Enseignant {teacher_name} supprimé avec succès')
        return redirect('teachers_list')

    # Compter les dépendances
    classes_count = Class.objects.filter(teacher=teacher).count()
    subjects_count = Subject.objects.filter(teacher=teacher).count()
    from .models import SubjectClass
    subject_classes_count = SubjectClass.objects.filter(teacher=teacher).count()

    context = {
        'teacher': teacher,
        'classes_count': classes_count,
        'subjects_count': subjects_count,
        'subject_classes_count': subject_classes_count,
    }
    return render(request, 'teachers/teacher_confirm_delete.html', context)


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


@login_required
def subject_edit(request, pk):
    """Modifier une matière"""
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        try:
            subject.name = request.POST.get('name')
            teacher_id = request.POST.get('teacher')
            subject.teacher_id = teacher_id if teacher_id else None
            subject.save()
            messages.success(request, f'Matière {subject.name} modifiée avec succès')
            return redirect('subjects_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')

    teachers = Teacher.objects.all()
    context = {'subject': subject, 'teachers': teachers}
    return render(request, 'subjects/subject_form.html', context)


@login_required
def subject_delete(request, pk):
    """Supprimer une matière"""
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Matière {subject_name} supprimée avec succès')
        return redirect('subjects_list')

    # Compter les dépendances
    from .models import SubjectClass
    classes_count = subject.classes.count()
    assignments_count = Assignment.objects.filter(subject=subject).count()
    subject_classes_count = SubjectClass.objects.filter(subject=subject).count()

    context = {
        'subject': subject,
        'classes_count': classes_count,
        'assignments_count': assignments_count,
        'subject_classes_count': subject_classes_count,
    }
    return render(request, 'subjects/subject_confirm_delete.html', context)


# ===================================
# GRADES VIEWS
# ===================================

@login_required
def grades_list(request):
    """Gestion des notes - Saisie groupée par classe et matière"""

    # Gérer la saisie groupée des notes
    if request.method == 'POST':
        print("=== DEBUT SAISIE GROUPEE NOTES ===")
        print("POST data:", request.POST)

        try:
            classe_id = request.POST.get('classe')
            subject_id = request.POST.get('subject')
            assignment_name = request.POST.get('assignment_name')
            evaluation_type = request.POST.get('evaluation_type', 'devoir')
            date_str = request.POST.get('date')

            print(f"Classe: {classe_id}, Matière: {subject_id}")
            print(f"Devoir: {assignment_name}, Type: {evaluation_type}")

            subject = Subject.objects.get(pk=subject_id)
            classe = Class.objects.get(pk=classe_id)

            # Récupérer la période active
            from .models import Period
            current_period = Period.objects.filter(is_active=True).first()

            # Créer l'assignment pour cette évaluation
            assignment = Assignment.objects.create(
                name=assignment_name,
                subject=subject,
                evaluation_type=evaluation_type,
                due_date=datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date(),
                points=20,
                period=current_period  # Associer à la période active
            )

            # Enregistrer les notes pour chaque élève
            notes_saved = 0
            for key, value in request.POST.items():
                if key.startswith('score_'):
                    student_id = key.replace('score_', '')
                    score = value.strip()

                    if score:  # Si une note a été saisie
                        student = Student.objects.get(pk=student_id)
                        Mark.objects.create(
                            student=student,
                            assignment=assignment,
                            score=float(score),
                            date=assignment.due_date
                        )
                        notes_saved += 1
                        print(f"Note enregistrée: {student.name} - {score}/20")

            print(f"=== {notes_saved} notes enregistrées ===")
            messages.success(request, f'{notes_saved} note(s) enregistrée(s) avec succès pour {assignment_name}')
            return redirect(f'/portal/grades/?class={classe_id}&subject={subject_id}')

        except Exception as e:
            print(f"=== ERREUR: {str(e)} ===")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur lors de la saisie des notes: {str(e)}')

    classes = Class.objects.all()
    all_subjects = Subject.objects.all()

    selected_class = request.GET.get('class')
    selected_subject = request.GET.get('subject')

    students_list = []
    class_obj = None
    subject_obj = None
    class_subjects = []

    # Si une classe est sélectionnée, récupérer ses matières et élèves
    if selected_class:
        class_obj = get_object_or_404(Class, pk=selected_class)
        class_subjects = class_obj.subject_set.all()

        # Si une matière est aussi sélectionnée, afficher les élèves
        if selected_subject:
            subject_obj = get_object_or_404(Subject, pk=selected_subject)
            students_query = class_obj.students.all().order_by('name', 'first_name')

            for student in students_query:
                # Récupérer les notes existantes pour cette matière
                marks = Mark.objects.filter(
                    student=student,
                    assignment__subject=subject_obj
                ).select_related('assignment').order_by('-date')

                students_list.append({
                    'id': student.id,
                    'matricule': student.matricule,
                    'name': student.name,
                    'first_name': student.first_name,
                    'full_name': f'{student.name} {student.first_name}',
                    'marks': marks,  # Historique des notes
                    'latest_mark': marks.first().score if marks.exists() else None,
                })

    context = {
        'classes': classes,
        'all_subjects': all_subjects,
        'class_subjects': class_subjects,
        'students_list': students_list,
        'selected_class': int(selected_class) if selected_class else None,
        'selected_subject': int(selected_subject) if selected_subject else None,
        'class_obj': class_obj,
        'subject_obj': subject_obj,
        'total_students': len(students_list),
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

        # Récupérer la période active
        from .models import Period
        current_period = Period.objects.filter(is_active=True).first()

        # Créer ou récupérer un assignment par défaut
        assignment, created = Assignment.objects.get_or_create(
            name=f'{subject.name} - Évaluation',
            subject=subject,
            defaults={
                'description': 'Évaluation générale',
                'due_date': datetime.now().date(),
                'points': 20,
                'period': current_period  # Associer à la période active
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
def delete_grade(request, mark_id):
    """Supprimer une note"""
    mark = get_object_or_404(Mark, pk=mark_id)

    if request.method == 'POST':
        student_name = f"{mark.student.name} {mark.student.first_name}"
        subject_name = mark.assignment.subject.name
        score = mark.score
        mark.delete()
        messages.success(request, f'Note de {student_name} en {subject_name} ({score}/20) supprimée avec succès')
        return redirect('grades_list')

    context = {'mark': mark}
    return render(request, 'grades/mark_confirm_delete.html', context)


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
    """Liste des bulletins avec options d'export"""
    # Filtres
    selected_class = request.GET.get('class')
    search = request.GET.get('search', '')

    students = Student.objects.all()

    # Filtrer par classe (relation inverse via Class.students)
    if selected_class:
        students = students.filter(class__id=selected_class)

    # Filtrer par recherche
    if search:
        students = students.filter(
            Q(name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(matricule__icontains=search)
        )

    students = students.order_by('name', 'first_name')

    classes = Class.objects.all()

    context = {
        'students': students,
        'classes': classes,
        'selected_class': int(selected_class) if selected_class else None,
        'search': search,
    }
    return render(request, 'grades/reports_list.html', context)


@login_required
def report_card(request, student_id):
    """Bulletin de notes d'un étudiant"""
    student = get_object_or_404(Student, pk=student_id)

    # Récupérer la classe de l'élève (relation ManyToMany inverse)
    student_class = student.class_set.first()

    # Importer les modèles nécessaires
    from .models import SubjectClass, Period

    # Récupérer la période active
    current_period = Period.objects.filter(is_active=True).first()

    # Si aucune période active, utiliser la plus récente
    if not current_period:
        current_period = Period.objects.order_by('-start_date').first()

    # Récupérer toutes les notes de l'étudiant pour la période active (uniquement devoirs et compositions)
    marks_filter = {
        'student': student,
        'assignment__evaluation_type__in': ['devoir', 'composition', 'Composition']
    }

    # Ajouter le filtre de période si une période existe
    if current_period:
        marks_filter['assignment__period'] = current_period

    marks = Mark.objects.filter(**marks_filter).select_related(
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
            # Récupérer le coefficient de la matière pour cette classe
            coefficient = 1  # Valeur par défaut
            teacher_name = f"{subject.teacher.name} {subject.teacher.first_name}" if subject.teacher else 'N/A'

            if student_class:
                # Chercher le coefficient dans SubjectClass
                try:
                    subject_class = SubjectClass.objects.get(subject=subject, classe=student_class)
                    coefficient = subject_class.coefficient
                    # Utiliser l'enseignant spécifique à la classe si défini
                    if subject_class.teacher:
                        teacher_name = f"{subject_class.teacher.name} {subject_class.teacher.first_name}"
                except SubjectClass.DoesNotExist:
                    # Utiliser le coefficient par défaut
                    pass

            subjects_dict[subject.name] = {
                'subject': subject.name,
                'teacher': teacher_name,
                'coefficient': coefficient,
                'scores': [],  # Liste de toutes les notes
                'rank': None,
            }

        # Ajouter la note à la liste des scores
        subjects_dict[subject.name]['scores'].append(mark.score)

    # Calculer la moyenne pour chaque matière
    for subject_data in subjects_dict.values():
        if subject_data['scores']:
            avg_score = sum(subject_data['scores']) / len(subject_data['scores'])
            subject_data['score'] = round(avg_score, 2)
            subject_data['total'] = round(avg_score * subject_data['coefficient'], 2)
        else:
            subject_data['score'] = 0
            subject_data['total'] = 0

    grades = list(subjects_dict.values())

    # Calculer les moyennes générales des trimestres précédents (une seule valeur par trimestre)
    previous_periods_general_averages = []
    if current_period:
        all_periods = Period.objects.filter(
            academic_year=current_period.academic_year
        ).order_by('start_date')

        # Calculer la moyenne générale pour chaque trimestre précédent
        for period in all_periods:
            if period.start_date < current_period.start_date:
                # Calculer la moyenne générale de l'étudiant pour ce trimestre
                period_general_avg = student.get_average(period=period)

                previous_periods_general_averages.append({
                    'period_name': period.get_name_display(),
                    'average': round(period_general_avg, 2) if period_general_avg is not None else '--'
                })

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

    # Calculer le rang dans la classe
    rank = student.get_rank_in_class()
    class_size = 0
    if student_class:
        class_students = student_class.students.all()
        class_size = class_students.count()

    # Récupérer les paramètres de l'école
    from .models import SchoolSettings
    try:
        school_settings = SchoolSettings.objects.first()
    except:
        school_settings = None

    # Récupérer les notes et moyennes des trimestres précédents
    previous_periods_data = []
    if current_period:
        # Récupérer tous les trimestres de l'année scolaire en cours, triés par date
        all_periods = Period.objects.filter(
            academic_year=current_period.academic_year
        ).order_by('start_date')

        # Identifier les trimestres précédents (avant la période actuelle)
        for period in all_periods:
            if period.start_date < current_period.start_date:
                # Récupérer les notes pour ce trimestre
                previous_marks = Mark.objects.filter(
                    student=student,
                    assignment__period=period,
                    assignment__evaluation_type__in=['devoir', 'composition', 'Composition']
                ).select_related('assignment__subject', 'assignment__subject__teacher')

                # Organiser les notes par matière pour ce trimestre
                previous_subjects_dict = {}
                for mark in previous_marks:
                    subject = mark.assignment.subject
                    if subject.name not in previous_subjects_dict:
                        # Récupérer le coefficient
                        coefficient = 1
                        teacher_name = f"{subject.teacher.name} {subject.teacher.first_name}" if subject.teacher else 'N/A'

                        if student_class:
                            try:
                                subject_class = SubjectClass.objects.get(subject=subject, classe=student_class)
                                coefficient = subject_class.coefficient
                                if subject_class.teacher:
                                    teacher_name = f"{subject_class.teacher.name} {subject_class.teacher.first_name}"
                            except SubjectClass.DoesNotExist:
                                pass

                        previous_subjects_dict[subject.name] = {
                            'subject': subject.name,
                            'teacher': teacher_name,
                            'coefficient': coefficient,
                            'scores': [],
                        }

                    previous_subjects_dict[subject.name]['scores'].append(mark.score)

                # Calculer les moyennes par matière
                previous_grades = []
                previous_total_points = 0
                previous_total_coefficients = 0

                for subject_data in previous_subjects_dict.values():
                    if subject_data['scores']:
                        avg_score = sum(subject_data['scores']) / len(subject_data['scores'])
                        subject_data['score'] = round(avg_score, 2)
                        subject_data['total'] = round(avg_score * subject_data['coefficient'], 2)
                    else:
                        subject_data['score'] = 0
                        subject_data['total'] = 0

                    previous_grades.append(subject_data)
                    previous_total_points += subject_data['total']
                    previous_total_coefficients += subject_data['coefficient']

                # Calculer la moyenne générale du trimestre
                previous_average = round(previous_total_points / previous_total_coefficients, 2) if previous_total_coefficients > 0 else 0

                # Ajouter à la liste des trimestres précédents
                if previous_marks.exists():  # Seulement si des notes existent
                    previous_periods_data.append({
                        'name': period.get_name_display(),
                        'grades': previous_grades,
                        'total_points': round(previous_total_points, 2),
                        'total_coefficients': previous_total_coefficients,
                        'average': previous_average
                    })

    # Calcul de la moyenne annuelle (uniquement pour le 3e trimestre ou 2e semestre)
    annual_average = None
    is_last_period = current_period and current_period.name in ['trimestre3', 'semestre2']
    if is_last_period:
        all_year_periods = Period.objects.filter(
            academic_year=current_period.academic_year
        ).order_by('start_date')

        period_averages = []
        for period in all_year_periods:
            if period.id == current_period.id:
                if average > 0:
                    period_averages.append(average)
            else:
                p_avg = student.get_average(period=period)
                if p_avg is not None:
                    period_averages.append(p_avg)

        if period_averages:
            annual_average = round(sum(period_averages) / len(period_averages), 2)

    # Décision du conseil (uniquement au 3e trimestre / 2e semestre)
    decision = None
    if is_last_period and annual_average is not None:
        if annual_average >= 10:
            decision = "Passé(e) en classe supérieure"
        elif annual_average <= 9.50:
            decision = "Redoublant(e)"
        # entre 9,50 et 10 : champ laissé vide pour décision du conseil

    context = {
        'student': {
            'full_name': f'{student.name} {student.first_name} {student.surname if student.surname else ""}',
            'matricule': student.matricule if student.matricule else f'ET-{student.id:04d}',
            'class': student_class.name if student_class else 'Non assigné',
            'birth_date': student.birth_date,
        },
        'grades': grades,
        'total_points': round(total_points, 2),
        'total_coefficients': total_coefficients,
        'average': average,
        'rank': rank,
        'class_size': class_size,
        'appreciation': appreciation,
        'school_name': school_settings.name if school_settings else 'ÉCOLE SECONDAIRE',
        'school_address': school_settings.address if school_settings else 'Ouagadougou, Burkina Faso',
        'school_phone': school_settings.phone if school_settings else '+226 XX XX XX XX',
        'school_logo': school_settings.logo.url if school_settings and school_settings.logo else None,
        'academic_year': current_period.academic_year if current_period else 'N/A',
        'period': current_period.get_name_display() if current_period else 'N/A',
        'class_teacher': f"{student_class.teacher.name} {student_class.teacher.first_name}" if student_class and student_class.teacher else 'Non assigné',
        'absences': None,
        'tardies': None,
        'current_date': datetime.now(),
        'previous_periods': previous_periods_data,  # Données complètes des trimestres précédents (notes + moyennes)
        'previous_periods_general_averages': previous_periods_general_averages,  # Moyennes générales des trimestres précédents
        'annual_average': annual_average,
        'is_last_period': is_last_period,
        'decision': decision,
    }

    return render(request, 'grades/report_card.html', context)


@login_required
def bulk_report_cards(request):
    """Génération en masse des bulletins pour une classe"""
    class_id = request.GET.get('class')

    if not class_id:
        messages.error(request, 'Veuillez sélectionner une classe')
        return redirect('reports_list')

    class_obj = get_object_or_404(Class, pk=class_id)
    students = class_obj.students.all().order_by('name', 'first_name')

    if not students.exists():
        messages.warning(request, 'Aucun élève dans cette classe')
        return redirect('reports_list')

    # Générer les données pour tous les élèves
    bulletins = []
    from .models import SchoolSettings, Period, SubjectClass

    # Obtenir ou créer les paramètres de l'école
    school_settings, _ = SchoolSettings.objects.get_or_create(
        defaults={
            'name': 'ÉCOLE SECONDAIRE',
            'address': 'Ouagadougou, Burkina Faso',
            'phone': '+226 XX XX XX XX'
        }
    )

    # Récupérer la période active
    current_period = Period.objects.filter(is_active=True).first()

    # Si aucune période active, utiliser la plus récente
    if not current_period:
        current_period = Period.objects.order_by('-start_date').first()

    # Calculer tous les rangs en une seule fois pour optimiser les performances
    rankings = class_obj.get_students_rankings(period=current_period)

    # Récupérer les trimestres précédents pour toute la classe
    previous_periods = []
    if current_period:
        all_periods = Period.objects.filter(
            academic_year=current_period.academic_year
        ).order_by('start_date')

        previous_periods = [p for p in all_periods if p.start_date < current_period.start_date]

    for student in students:
        student_class = student.class_set.first()

        # Filtrer les notes par période active
        marks_filter = {
            'student': student,
            'assignment__evaluation_type__in': ['devoir', 'composition', 'Composition']
        }

        if current_period:
            marks_filter['assignment__period'] = current_period

        marks = Mark.objects.filter(**marks_filter).select_related(
            'assignment__subject', 'assignment__subject__teacher'
        )

        grades = []
        total_points = 0
        total_coefficients = 0

        subjects_dict = {}
        for mark in marks:
            subject = mark.assignment.subject
            if subject.name not in subjects_dict:
                coefficient = 1
                teacher_name = f"{subject.teacher.name} {subject.teacher.first_name}" if subject.teacher else 'N/A'

                if student_class:
                    try:
                        subject_class = SubjectClass.objects.get(subject=subject, classe=student_class)
                        coefficient = subject_class.coefficient
                        if subject_class.teacher:
                            teacher_name = f"{subject_class.teacher.name} {subject_class.teacher.first_name}"
                    except SubjectClass.DoesNotExist:
                        pass

                subjects_dict[subject.name] = {
                    'subject': subject.name,
                    'teacher': teacher_name,
                    'coefficient': coefficient,
                    'scores': [],  # Liste de toutes les notes
                    'rank': None,
                }

            # Ajouter la note à la liste des scores
            subjects_dict[subject.name]['scores'].append(mark.score)

        # Calculer la moyenne pour chaque matière
        for subject_data in subjects_dict.values():
            if subject_data['scores']:
                avg_score = sum(subject_data['scores']) / len(subject_data['scores'])
                subject_data['score'] = round(avg_score, 2)
                subject_data['total'] = round(avg_score * subject_data['coefficient'], 2)
            else:
                subject_data['score'] = 0
                subject_data['total'] = 0

        grades = list(subjects_dict.values())

        # Calculer les moyennes générales des trimestres précédents (une seule valeur par trimestre)
        previous_periods_general_averages = []
        if current_period:
            for period in previous_periods:
                # Calculer la moyenne générale de l'étudiant pour ce trimestre
                period_general_avg = student.get_average(period=period)

                previous_periods_general_averages.append({
                    'period_name': period.get_name_display(),
                    'average': round(period_general_avg, 2) if period_general_avg is not None else '--'
                })

        for grade in grades:
            total_points += grade['total']
            total_coefficients += grade['coefficient']

        average = round(total_points / total_coefficients, 2) if total_coefficients > 0 else 0
        if average >= 17:
            appreciation = "Tableau d'honneur"
        if average >= 15:
            appreciation = "Excellent élève. Travail remarquable. Continuez ainsi!"
        elif average >= 14:
            appreciation = "Résultats très satisfaisants. Poursuivez vos efforts."
        elif average >= 12:
            appreciation = "Résultats  satisfaisants. Poursuivez vos efforts."
        elif average >= 10:
            appreciation = "Passable. Efforts à poursuivre."
        else:
            appreciation = "Résultats insuffisants. Travail et concentration nécessaires."

        # Récupérer les notes et moyennes des trimestres précédents pour cet étudiant
        student_previous_periods_data = []
        for period in previous_periods:
            # Récupérer les notes pour ce trimestre
            previous_marks = Mark.objects.filter(
                student=student,
                assignment__period=period,
                assignment__evaluation_type__in=['devoir', 'composition', 'Composition']
            ).select_related('assignment__subject', 'assignment__subject__teacher')

            # Organiser les notes par matière pour ce trimestre
            previous_subjects_dict = {}
            for mark in previous_marks:
                subject = mark.assignment.subject
                if subject.name not in previous_subjects_dict:
                    # Récupérer le coefficient
                    coefficient = 1
                    teacher_name = f"{subject.teacher.name} {subject.teacher.first_name}" if subject.teacher else 'N/A'

                    if student_class:
                        try:
                            subject_class = SubjectClass.objects.get(subject=subject, classe=student_class)
                            coefficient = subject_class.coefficient
                            if subject_class.teacher:
                                teacher_name = f"{subject_class.teacher.name} {subject_class.teacher.first_name}"
                        except SubjectClass.DoesNotExist:
                            pass

                    previous_subjects_dict[subject.name] = {
                        'subject': subject.name,
                        'teacher': teacher_name,
                        'coefficient': coefficient,
                        'scores': [],
                    }

                previous_subjects_dict[subject.name]['scores'].append(mark.score)

            # Calculer les moyennes par matière
            previous_grades = []
            previous_total_points = 0
            previous_total_coefficients = 0

            for subject_data in previous_subjects_dict.values():
                if subject_data['scores']:
                    avg_score = sum(subject_data['scores']) / len(subject_data['scores'])
                    subject_data['score'] = round(avg_score, 2)
                    subject_data['total'] = round(avg_score * subject_data['coefficient'], 2)
                else:
                    subject_data['score'] = 0
                    subject_data['total'] = 0

                previous_grades.append(subject_data)
                previous_total_points += subject_data['total']
                previous_total_coefficients += subject_data['coefficient']

            # Calculer la moyenne générale du trimestre
            previous_average = round(previous_total_points / previous_total_coefficients, 2) if previous_total_coefficients > 0 else 0

            # Ajouter à la liste des trimestres précédents
            if previous_marks.exists():  # Seulement si des notes existent
                student_previous_periods_data.append({
                    'name': period.get_name_display(),
                    'grades': previous_grades,
                    'total_points': round(previous_total_points, 2),
                    'total_coefficients': previous_total_coefficients,
                    'average': previous_average
                })

        # Calcul de la moyenne annuelle (uniquement pour le 3e trimestre ou 2e semestre)
        student_annual_average = None
        is_last_period = current_period and current_period.name in ['trimestre3', 'semestre2']
        if is_last_period:
            all_year_periods = Period.objects.filter(
                academic_year=current_period.academic_year
            ).order_by('start_date')

            period_averages = []
            for period in all_year_periods:
                if period.id == current_period.id:
                    if average > 0:
                        period_averages.append(average)
                else:
                    p_avg = student.get_average(period=period)
                    if p_avg is not None:
                        period_averages.append(p_avg)

            if period_averages:
                student_annual_average = round(sum(period_averages) / len(period_averages), 2)

        # Décision du conseil (uniquement au 3e trimestre / 2e semestre)
        student_decision = None
        if is_last_period and student_annual_average is not None:
            if student_annual_average >= 10:
                student_decision = "Passé(e) en classe supérieure"
            elif student_annual_average <= 9.50:
                student_decision = "Redoublant(e)"

        bulletins.append({
            'student': {
                'full_name': f'{student.name} {student.first_name} {student.surname if student.surname else ""}',
                'matricule': student.matricule if student.matricule else f'ET-{student.id:04d}',
                'class': student_class.name if student_class else 'Non assigné',
                'birth_date': student.birth_date,
                'absence': getattr(student, 'absence', None),
                'retard': getattr(student, 'retard', None),
            },
            'grades': grades,
            'total_points': round(total_points, 2),
            'total_coefficient': total_coefficients,
            'average': average,
            'appreciation': appreciation,
            'rank': rankings.get(student.id),
            'class_size': students.count(),
            'previous_periods': student_previous_periods_data,  # Données complètes des trimestres précédents
            'previous_periods_general_averages': previous_periods_general_averages,  # Moyennes générales des trimestres précédents
            'annual_average': student_annual_average,
            'decision': student_decision,
        })

    context = {
        'bulletins': bulletins,
        'class_obj': class_obj,
        'class_name': class_obj.name,
        'school_settings': school_settings,
        'current_year': current_period.academic_year if current_period else 'N/A',
        'academic_year': current_period.academic_year if current_period else 'N/A',
        'period': current_period.get_name_display() if current_period else 'N/A',
        'class_teacher': f"{class_obj.teacher.name} {class_obj.teacher.first_name}" if class_obj.teacher else 'Non assigné',
        'class_size': students.count(),
        'current_date': datetime.now(),
        'is_last_period': current_period and current_period.name in ['trimestre3', 'semestre2'],
    }

    return render(request, 'grades/bulk_report_cards.html', context)


# ===================================
# PERIODS MANAGEMENT VIEWS
# ===================================

@login_required
def periods_list(request):
    """Liste et gestion des périodes scolaires"""
    from .models import Period

    periods = Period.objects.all().order_by('-academic_year', 'start_date')

    context = {
        'periods': periods,
        'page_title': 'Gestion des Périodes',
    }

    return render(request, 'periods/periods_list.html', context)


@login_required
@require_POST
def activate_period(request, period_id):
    """Active une période et désactive toutes les autres"""
    from .models import Period

    try:
        # Récupérer la période
        period = get_object_or_404(Period, id=period_id)

        # Désactiver toutes les périodes
        Period.objects.all().update(is_active=False)

        # Activer la période sélectionnée
        period.is_active = True
        period.save()

        messages.success(
            request,
            f'Période "{period.get_name_display()} - {period.academic_year}" activée avec succès!'
        )

    except Exception as e:
        messages.error(request, f'Erreur lors de l\'activation de la période: {str(e)}')

    return redirect('periods_list')


@login_required
def period_create(request):
    """Créer une nouvelle période"""
    from .models import Period
    from django import forms

    class PeriodForm(forms.ModelForm):
        class Meta:
            model = Period
            fields = ['name', 'academic_year', 'start_date', 'end_date', 'is_active']
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'name': forms.Select(attrs={'class': 'form-control'}),
                'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-2026'}),
                'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)

            # Si cette période est activée, désactiver toutes les autres
            if period.is_active:
                Period.objects.all().update(is_active=False)

            period.save()
            messages.success(request, f'Période "{period.get_name_display()}" créée avec succès!')
            return redirect('periods_list')
    else:
        form = PeriodForm()

    context = {
        'form': form,
        'page_title': 'Créer une Période',
        'submit_text': 'Créer',
    }

    return render(request, 'periods/period_form.html', context)


@login_required
def period_edit(request, period_id):
    """Modifier une période existante"""
    from .models import Period
    from django import forms

    period = get_object_or_404(Period, id=period_id)

    class PeriodForm(forms.ModelForm):
        class Meta:
            model = Period
            fields = ['name', 'academic_year', 'start_date', 'end_date', 'is_active']
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'name': forms.Select(attrs={'class': 'form-control'}),
                'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
                'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

    if request.method == 'POST':
        form = PeriodForm(request.POST, instance=period)
        if form.is_valid():
            updated_period = form.save(commit=False)

            # Si cette période est activée, désactiver toutes les autres
            if updated_period.is_active:
                Period.objects.exclude(id=period_id).update(is_active=False)

            updated_period.save()
            messages.success(request, f'Période "{period.get_name_display()}" modifiée avec succès!')
            return redirect('periods_list')
    else:
        form = PeriodForm(instance=period)

    context = {
        'form': form,
        'period': period,
        'page_title': f'Modifier la Période: {period.get_name_display()}',
        'submit_text': 'Mettre à jour',
    }

    return render(request, 'periods/period_form.html', context)


@login_required
@require_POST
def period_delete(request, period_id):
    """Supprimer une période"""
    from .models import Period

    period = get_object_or_404(Period, id=period_id)
    period_name = period.get_name_display()

    try:
        period.delete()
        messages.success(request, f'Période "{period_name}" supprimée avec succès!')
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return redirect('periods_list')
