"""
Commande Django pour changer la période active
Usage: python manage.py set_active_period <periode_id>
       python manage.py set_active_period --list
       python manage.py set_active_period --year 2025-2026 --period trimestre2
"""
from django.core.management.base import BaseCommand, CommandError
from school_portal.models import Period


class Command(BaseCommand):
    help = 'Active une période spécifique et désactive toutes les autres'

    def add_arguments(self, parser):
        # Argument positionnel pour l'ID de la période
        parser.add_argument(
            'period_id',
            nargs='?',
            type=int,
            help='ID de la période à activer'
        )

        # Option pour lister toutes les périodes
        parser.add_argument(
            '--list',
            action='store_true',
            help='Lister toutes les périodes disponibles'
        )

        # Option pour sélectionner par année et nom
        parser.add_argument(
            '--year',
            type=str,
            help='Année scolaire (ex: 2025-2026)'
        )

        parser.add_argument(
            '--period',
            type=str,
            choices=['trimestre1', 'trimestre2', 'trimestre3', 'semestre1', 'semestre2'],
            help='Nom de la période'
        )

    def handle(self, *args, **options):
        # Option 1: Lister toutes les périodes
        if options['list']:
            self.list_periods()
            return

        # Option 2: Activer par année et nom de période
        if options['year'] and options['period']:
            self.activate_by_name(options['year'], options['period'])
            return

        # Option 3: Activer par ID
        if options['period_id']:
            self.activate_by_id(options['period_id'])
            return

        # Si aucune option, afficher l'aide
        self.stdout.write(self.style.ERROR('Erreur: Veuillez spécifier une période'))
        self.stdout.write('')
        self.stdout.write('Usage:')
        self.stdout.write('  python manage.py set_active_period --list')
        self.stdout.write('  python manage.py set_active_period <period_id>')
        self.stdout.write('  python manage.py set_active_period --year 2025-2026 --period trimestre2')

    def list_periods(self):
        """Affiche toutes les périodes disponibles"""
        periods = Period.objects.all().order_by('-academic_year', 'start_date')

        if not periods.exists():
            self.stdout.write(self.style.WARNING('Aucune période trouvée'))
            return

        self.stdout.write(self.style.SUCCESS('Périodes disponibles:'))
        self.stdout.write('=' * 80)

        current_year = None
        for period in periods:
            # Afficher l'année scolaire comme en-tête
            if period.academic_year != current_year:
                current_year = period.academic_year
                self.stdout.write('')
                self.stdout.write(self.style.WARNING(f'Année Scolaire: {current_year}'))
                self.stdout.write('-' * 80)

            # Indicateur de période active
            status = self.style.SUCCESS('ACTIVE') if period.is_active else ''

            # Afficher les détails de la période
            self.stdout.write(
                f'  ID: {period.id:<4} | '
                f'{period.get_name_display():<20} | '
                f'{period.start_date.strftime("%d/%m/%Y")} - {period.end_date.strftime("%d/%m/%Y")} | '
                f'{status}'
            )

    def activate_by_id(self, period_id):
        """Active une période par son ID"""
        try:
            # Récupérer la période
            period = Period.objects.get(id=period_id)

            # Désactiver toutes les autres périodes
            Period.objects.all().update(is_active=False)

            # Activer la période sélectionnée
            period.is_active = True
            period.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Période activée: {period.get_name_display()} ({period.academic_year})'
                )
            )
            self.stdout.write(
                f'  Début: {period.start_date.strftime("%d/%m/%Y")}'
            )
            self.stdout.write(
                f'  Fin: {period.end_date.strftime("%d/%m/%Y")}'
            )

        except Period.DoesNotExist:
            raise CommandError(f'Période avec ID {period_id} introuvable')

    def activate_by_name(self, year, period_name):
        """Active une période par son année et son nom"""
        try:
            # Récupérer la période
            period = Period.objects.get(
                academic_year=year,
                name=period_name
            )

            # Désactiver toutes les autres périodes
            Period.objects.all().update(is_active=False)

            # Activer la période sélectionnée
            period.is_active = True
            period.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Période activée: {period.get_name_display()} ({period.academic_year})'
                )
            )
            self.stdout.write(
                f'  Début: {period.start_date.strftime("%d/%m/%Y")}'
            )
            self.stdout.write(
                f'  Fin: {period.end_date.strftime("%d/%m/%Y")}'
            )

        except Period.DoesNotExist:
            raise CommandError(
                f'Période "{period_name}" pour l\'année {year} introuvable'
            )
