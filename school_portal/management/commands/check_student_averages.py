"""
Commande Django pour vérifier les moyennes d'un étudiant pour tous les trimestres
Usage: python manage.py check_student_averages <student_id>
       python manage.py check_student_averages --all
"""
from django.core.management.base import BaseCommand, CommandError
from school_portal.models import Student, Period, Mark


class Command(BaseCommand):
    help = 'Vérifie les moyennes d\'un étudiant pour tous les trimestres'

    def add_arguments(self, parser):
        parser.add_argument(
            'student_id',
            nargs='?',
            type=int,
            help='ID de l\'étudiant'
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='Afficher les moyennes de tous les étudiants'
        )

        parser.add_argument(
            '--year',
            type=str,
            help='Filtrer par année scolaire (ex: 2025-2026)'
        )

    def handle(self, *args, **options):
        if options['all']:
            self.show_all_students(options.get('year'))
        elif options['student_id']:
            self.show_student_averages(options['student_id'], options.get('year'))
        else:
            self.stdout.write(self.style.ERROR('Erreur: Spécifiez un student_id ou --all'))
            self.stdout.write('')
            self.stdout.write('Usage:')
            self.stdout.write('  python manage.py check_student_averages 1')
            self.stdout.write('  python manage.py check_student_averages --all')
            self.stdout.write('  python manage.py check_student_averages --all --year 2025-2026')

    def show_student_averages(self, student_id, year_filter=None):
        """Affiche les moyennes d'un étudiant pour tous les trimestres"""
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise CommandError(f'Étudiant avec ID {student_id} introuvable')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'   MOYENNES DE {student.name} {student.first_name}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Récupérer toutes les périodes
        periods = Period.objects.all().order_by('-academic_year', 'start_date')

        if year_filter:
            periods = periods.filter(academic_year=year_filter)

        if not periods.exists():
            self.stdout.write(self.style.WARNING('Aucune période trouvée'))
            return

        current_year = None
        for period in periods:
            # Afficher l'année scolaire comme en-tête
            if period.academic_year != current_year:
                current_year = period.academic_year
                self.stdout.write('')
                self.stdout.write(self.style.WARNING(f'Année Scolaire: {current_year}'))
                self.stdout.write('-' * 70)

            # Calculer la moyenne pour cette période
            average = student.get_average(period=period)

            # Compter les notes pour cette période
            marks_count = Mark.objects.filter(
                student=student,
                assignment__period=period,
                assignment__evaluation_type__in=['devoir', 'composition', 'Composition']
            ).count()

            # Affichage
            status_icon = '✓ ACTIVE' if period.is_active else ''

            if average is not None:
                avg_display = f'{average}/20'
                status = self.style.SUCCESS(avg_display)
            else:
                avg_display = 'Aucune note'
                status = self.style.WARNING(avg_display)

            self.stdout.write(
                f'  {period.get_name_display():<20} | '
                f'{status:<15} | '
                f'{marks_count} note(s) | '
                f'{status_icon}'
            )

        self.stdout.write('')
        self.stdout.write('-' * 70)

        # Vérifier s'il y a des notes sans période
        marks_without_period = Mark.objects.filter(
            student=student,
            assignment__period__isnull=True
        ).count()

        if marks_without_period > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'⚠️  ATTENTION: {marks_without_period} note(s) ne sont pas associées à une période!'
                )
            )

        self.stdout.write('')

    def show_all_students(self, year_filter=None):
        """Affiche les moyennes de tous les étudiants"""
        students = Student.objects.all().order_by('name', 'first_name')

        if not students.exists():
            self.stdout.write(self.style.WARNING('Aucun étudiant trouvé'))
            return

        # Récupérer les périodes
        periods = Period.objects.all().order_by('-academic_year', 'start_date')
        if year_filter:
            periods = periods.filter(academic_year=year_filter)

        if not periods.exists():
            self.stdout.write(self.style.WARNING('Aucune période trouvée'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 90))
        self.stdout.write(self.style.SUCCESS('   MOYENNES DE TOUS LES ÉTUDIANTS'))
        self.stdout.write(self.style.SUCCESS('=' * 90))
        self.stdout.write('')

        # En-tête du tableau
        header = f"{'Étudiant':<30} | "
        for period in periods:
            header += f"{period.get_name_display()[:15]:<15} | "
        self.stdout.write(header)
        self.stdout.write('-' * 90)

        # Données pour chaque étudiant
        for student in students:
            row = f"{student.name} {student.first_name}"[:30]
            row = f"{row:<30} | "

            for period in periods:
                average = student.get_average(period=period)
                if average is not None:
                    avg_text = f"{average}/20"
                else:
                    avg_text = "--"
                row += f"{avg_text:<15} | "

            self.stdout.write(row)

        self.stdout.write('')
