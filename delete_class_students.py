"""
Script pour supprimer tous les élèves d'une classe
Usage: python delete_class_students.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
django.setup()

from school_portal.models import Student, Class

def delete_students_from_class(class_name):
    """Supprimer tous les élèves d'une classe"""

    try:
        classe = Class.objects.get(name=class_name)
        print(f"\n>> Classe trouvee: {classe.name}")
    except Class.DoesNotExist:
        print(f"\nX Classe '{class_name}' non trouvee!")
        print("Classes disponibles:")
        for c in Class.objects.all():
            print(f"  - {c.name}")
        return

    # Récupérer tous les élèves de la classe
    students = classe.students.all()
    count = students.count()

    if count == 0:
        print(f"\n! Aucun eleve dans la classe {class_name}")
        return

    print(f"\n>> {count} eleve(s) trouve(s) dans la classe {class_name}")
    print(">> Suppression en cours...")

    # Supprimer tous les élèves
    deleted = 0
    for student in students:
        print(f"  - Suppression: {student.name} {student.first_name} (Matricule: {student.matricule})")
        student.delete()
        deleted += 1

    print(f"\n{'='*60}")
    print(f">> RESUME:")
    print(f"  - Eleves supprimes: {deleted}")
    print(f"  ** Classe: {class_name}")
    print(f"{'='*60}\n")

def main():
    print("="*60)
    print("  SUPPRESSION DES ELEVES D'UNE CLASSE")
    print("="*60)

    # Nom de la classe
    class_name = "3ème "  # Avec l'espace

    delete_students_from_class(class_name)

    print("OK Script termine!")

if __name__ == '__main__':
    main()
