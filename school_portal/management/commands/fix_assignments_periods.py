"""
Commande Django pour associer les assignments (devoirs) sans période à une période appropriée
Usage: python manage.py fix_assignments_periods
"""
from django.core.management.base import BaseCommand, CommandError
from school_portal.models import Assignment, Period
from datetime import datetime


class Command(BaseCommand):
    help = 'Associe les assignments sans période à la période appropriée en fonction de leur date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=int,
            help='ID de la période à associer à tous les assignments sans période'
        )

        parser.add_argument(
            '--auto',
            action='store_true',
            help='Associe automatiquement chaque assignment à la période correspondant à sa date'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans modifier la base de données'
        )

    def handle(self, *args, **options):
        period_id = options.get('period')
        auto_assign = options.get('auto')
        dry_run = options.get('dry_run')

        # Récupérer tous les assignments sans période
        assignments_without_period = Assignment.objects.filter(period__isnull=True)
        count = assignments_without_period.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('✓ Aucun assignment sans période trouvé'))
            return

        self.stdout.write(f'Trouvé {count} assignment(s) sans période')
        self.stdout.write('')

        if dry_run:
            self.stdout.write(self.style.WARNING('MODE TEST (dry-run) - Aucune modification ne sera effectuée'))
            self.stdout.write('')

        # Si un ID de période spécifique est fourni
        if period_id:
            try:
                period = Period.objects.get(id=period_id)
                self.stdout.write(f'Association à la période: {period.get_name_display()} ({period.academic_year})')
                self.stdout.write('')

                updated_count = 0
                for assignment in assignments_without_period:
                    self.stdout.write(f'  • {assignment.name} ({assignment.subject.name}) - {assignment.due_date}')
                    if not dry_run:
                        assignment.period = period
                        assignment.save()
                    updated_count += 1

                if not dry_run:
                    self.stdout.write('')
                    self.stdout.write(self.style.SUCCESS(f'✓ {updated_count} assignment(s) mis à jour'))
                else:
                    self.stdout.write('')
                    self.stdout.write(self.style.WARNING(f'[DRY-RUN] {updated_count} assignment(s) seraient mis à jour'))

            except Period.DoesNotExist:
                raise CommandError(f'Période avec ID {period_id} introuvable')

        # Si mode automatique basé sur les dates
        elif auto_assign:
            periods = Period.objects.all().order_by('start_date')
            if not periods.exists():
                raise CommandError('Aucune période trouvée. Créez d\'abord des périodes avec setup_periods')

            self.stdout.write('Association automatique basée sur les dates:')
            self.stdout.write('')

            updated_count = 0
            unmatched_count = 0

            for assignment in assignments_without_period:
                # Trouver la période appropriée
                matched_period = None
                for period in periods:
                    if period.start_date <= assignment.due_date <= period.end_date:
                        matched_period = period
                        break

                if matched_period:
                    self.stdout.write(
                        f'  ✓ {assignment.name} ({assignment.subject.name}) - {assignment.due_date} '
                        f'→ {matched_period.get_name_display()}'
                    )
                    if not dry_run:
                        assignment.period = matched_period
                        assignment.save()
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ✗ {assignment.name} ({assignment.subject.name}) - {assignment.due_date} '
                            f'→ Aucune période correspondante'
                        )
                    )
                    unmatched_count += 1

            self.stdout.write('')
            if not dry_run:
                self.stdout.write(self.style.SUCCESS(f'✓ {updated_count} assignment(s) mis à jour'))
            else:
                self.stdout.write(self.style.WARNING(f'[DRY-RUN] {updated_count} assignment(s) seraient mis à jour'))

            if unmatched_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {unmatched_count} assignment(s) n\'ont pas pu être associés')
                )

        # Si aucune option, afficher les assignments et les périodes disponibles
        else:
            self.stdout.write('Assignments sans période:')
            self.stdout.write('')
            for assignment in assignments_without_period:
                self.stdout.write(
                    f'  • {assignment.name} ({assignment.subject.name}) - {assignment.due_date}'
                )

            self.stdout.write('')
            self.stdout.write('Périodes disponibles:')
            self.stdout.write('')

            periods = Period.objects.all().order_by('-academic_year', 'start_date')
            for period in periods:
                active = self.style.SUCCESS(' [ACTIVE]') if period.is_active else ''
                self.stdout.write(
                    f'  {period.id}. {period.get_name_display()} - {period.academic_year} '
                    f'({period.start_date} → {period.end_date}){active}'
                )

            self.stdout.write('')
            self.stdout.write('Options:')
            self.stdout.write('  --period <ID>  : Associer tous les assignments à la période spécifiée')
            self.stdout.write('  --auto         : Associer automatiquement selon les dates')
            self.stdout.write('  --dry-run      : Tester sans modifier la base de données')
            self.stdout.write('')
            self.stdout.write('Exemples:')
            self.stdout.write('  python manage.py fix_assignments_periods --period 2')
            self.stdout.write('  python manage.py fix_assignments_periods --auto')
            self.stdout.write('  python manage.py fix_assignments_periods --auto --dry-run')
