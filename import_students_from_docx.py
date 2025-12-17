"""
Script d'importation des lves depuis un fichier Word (.docx)
Usage: python import_students_from_docx.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
django.setup()

from school_portal.models import Student, Class

try:
    from docx import Document
except ImportError:
    print("Installation de python-docx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document


def parse_date(date_str):
    """Parse diffrents formats de date"""
    if not date_str or date_str.strip() == '':
        return None

    date_str = date_str.strip()
    formats = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d.%m.%Y',
        '%Y-%m-%d',
        '%d/%m/%y',
        '%d-%m-%y',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    print(f"\! Format de date non reconnu: {date_str}")
    return None


def extract_students_from_docx(file_path):
    """
    Extraire les informations des lves depuis un fichier Word
    Format attendu dans le document:
    - Tableau avec colonnes: N, Nom, Prnom(s), Date de naissance, etc.
    - Ou liste avec format: Nom Prnom - Date
    """
    print(f">> Lecture du fichier: {file_path}")
    doc = Document(file_path)

    students = []

    # Mthode 1: Extraire depuis les tableaux
    for table in doc.tables:
        print(f"\n>> Tableau trouve avec {len(table.rows)} lignes")

        # Afficher les en-ttes pour debug
        if len(table.rows) > 0:
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            print(f"En-ttes: {headers}")

        # Parcourir les lignes (en sautant l'en-tte)
        for i, row in enumerate(table.rows[1:], start=1):
            cells = [cell.text.strip() for cell in row.cells]

            # Ignorer les lignes vides
            if not any(cells):
                continue

            # Adapter selon la structure du tableau
            # Format attendu: N, Nom, Prnom(s), Date de naissance
            if len(cells) >= 3:
                num = cells[0] if len(cells) > 0 else ''
                nom = cells[1] if len(cells) > 1 else ''
                prenom = cells[2] if len(cells) > 2 else ''
                date_naissance = cells[4] if len(cells) > 4 else ''

                # Ignorer si pas de nom ou prnom
                if not nom or not prenom:
                    continue

                student_data = {
                    'numero': num,
                    'name': nom.upper(),
                    'first_name': prenom.title(),
                    'birth_date': parse_date(date_naissance),
                }

                students.append(student_data)
                print(f"  + {i}. {nom} {prenom} - {date_naissance}")

    # Mthode 2: Extraire depuis les paragraphes si pas de tableau
    if not students:
        print("\n Aucun tableau trouv, lecture des paragraphes...")
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text or len(text) < 5:
                continue

            # Format: "1. NOM Prnom - 01/01/2000"
            # ou: "NOM Prnom 01/01/2000"
            print(f"  Ligne: {text}")

    return students


def import_students_to_class(students, class_name):
    """Importer les lves dans une classe"""

    # Rcuprer ou crer la classe
    try:
        classe = Class.objects.get(name=class_name)
        print(f"\nOK Classe trouve: {classe.name}")
    except Class.DoesNotExist:
        print(f"\nX Classe '{class_name}' non trouve!")
        print("Classes disponibles:")
        for c in Class.objects.all():
            print(f"  - {c.name}")
        return 0

    imported = 0
    errors = 0

    print(f"\n>> Import de {len(students)} lves dans la classe {class_name}...\n")

    for student_data in students:
        try:
            # Crer l'lve
            student = Student.objects.create(
                name=student_data['name'],
                first_name=student_data['first_name'],
                surname='',
                birth_date=student_data.get('birth_date'),
                email='',
                phone='',
                address='',
            )

            # Assigner  la classe
            classe.students.add(student)

            imported += 1
            print(f"+ {imported}. {student.name} {student.first_name} (Matricule: {student.matricule})")

        except Exception as e:
            errors += 1
            print(f"- Erreur pour {student_data.get('name')} {student_data.get('first_name')}: {str(e)}")

    print(f"\n{'='*60}")
    print(f">> RSUM:")
    print(f"  + Imports: {imported}")
    print(f"  - Erreurs: {errors}")
    print(f"  ** Classe: {class_name}")
    print(f"{'='*60}\n")

    return imported


def main():
    """Fonction principale"""
    print("="*60)
    print("  IMPORTATION DES LVES DEPUIS UN FICHIER WORD")
    print("="*60)

    # Chemin du fichier Word
    file_path = r"C:\Users\autom\Documents\Oasis\LYCEE PRIVE OASIS DU SAVOIR                                                                                                 ANNEE SCOLAIRE 2025.docx"

    # Nom de la classe cible
    class_name = "3ème "  # Modifier si ncessaire (noter l'espace  la fin)

    # Vrifier que le fichier existe
    if not os.path.exists(file_path):
        print(f"X Fichier non trouv: {file_path}")
        return

    # Extraire les lves du document
    students = extract_students_from_docx(file_path)

    if not students:
        print("\n\! Aucun lve trouv dans le document!")
        print("\nFormat attendu dans le document Word:")
        print("  - Tableau avec colonnes: N, Nom, Prnom(s), Date de naissance")
        print("  - Ou liste textuelle avec format: NOM Prnom - Date")
        return

    print(f"\nOK {len(students)} lve(s) extrait(s) du document")

    # Confirmer l'import (auto-accepté en mode non-interactif)
    print(f"\n>> Import automatique dans la classe '{class_name}'...")

    # Importer dans la base de donnes
    import_students_to_class(students, class_name)

    print("OK Script terminé!")


if __name__ == '__main__':
    main()
