"""
Commande Django pour créer automatiquement les périodes d'une année scolaire
Usage: python manage.py setup_periods <année_scolaire>
       python manage.py setup_periods 2025-2026 --type trimestre
       python manage.py setup_periods 2025-2026 --type semestre
"""
from django.core.management.base import BaseCommand, CommandError
from school_portal.models import Period
from datetime import date


class Command(BaseCommand):
    help = 'Crée automatiquement les périodes pour une année scolaire'

    def add_arguments(self, parser):
        parser.add_argument(
            'academic_year',
            type=str,
            help='Année scolaire (ex: 2025-2026)'
        )

        parser.add_argument(
            '--type',
            type=str,
            choices=['trimestre', 'semestre'],
            default='trimestre',
            help='Type de périodes (trimestre ou semestre)'
        )

        parser.add_argument(
            '--activate-first',
            action='store_true',
            help='Activer automatiquement la première période'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprimer les périodes existantes pour cette année avant de créer'
        )

    def handle(self, *args, **options):
        academic_year = options['academic_year']
        period_type = options['type']
        activate_first = options['activate_first']
        force = options['force']

        # Validation du format d'année
        if not self.validate_year_format(academic_year):
            raise CommandError(
                'Format d\'année invalide. Utilisez le format: 2025-2026'
            )

        # Extraire les années
        start_year, end_year = map(int, academic_year.split('-'))

        # Vérifier si des périodes existent déjà
        existing = Period.objects.filter(academic_year=academic_year)
        if existing.exists():
            if force:
                count = existing.count()
                existing.delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'✓ {count} période(s) existante(s) supprimée(s)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Attention: {existing.count()} période(s) existent déjà pour {academic_year}'
                    )
                )
                self.stdout.write('Utilisez --force pour les supprimer et recréer')
                return

        # Désactiver toutes les périodes si on doit activer la première
        if activate_first:
            Period.objects.all().update(is_active=False)

        # Créer les périodes selon le type
        if period_type == 'trimestre':
            self.create_trimesters(academic_year, start_year, end_year, activate_first)
        else:
            self.create_semesters(academic_year, start_year, end_year, activate_first)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✓ Paramétrage terminé avec succès!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write('Prochaines étapes:')
        self.stdout.write('  1. Vérifiez les périodes: python manage.py set_active_period --list')
        self.stdout.write('  2. Ou accédez à: http://localhost:8000/periods/')
        self.stdout.write('  3. Associez vos devoirs aux périodes lors de leur création')

    def validate_year_format(self, year):
        """Valide le format de l'année scolaire"""
        try:
            parts = year.split('-')
            if len(parts) != 2:
                return False
            start, end = map(int, parts)
            return end == start + 1
        except:
            return False

    def create_trimesters(self, academic_year, start_year, end_year, activate_first):
        """Crée les 3 trimestres de l'année scolaire"""
        self.stdout.write(
            self.style.SUCCESS(f'\nCréation des trimestres pour {academic_year}')
        )
        self.stdout.write('-' * 70)

        trimesters = [
            {
                'name': 'trimestre1',
                'display': '1er Trimestre',
                'start': date(start_year, 9, 1),
                'end': date(start_year, 12, 15),
            },
            {
                'name': 'trimestre2',
                'display': '2e Trimestre',
                'start': date(end_year, 1, 5),
                'end': date(end_year, 3, 30),
            },
            {
                'name': 'trimestre3',
                'display': '3e Trimestre',
                'start': date(end_year, 4, 1),
                'end': date(end_year, 6, 30),
            },
        ]

        for idx, trim in enumerate(trimesters):
            is_active = activate_first and idx == 0

            period = Period.objects.create(
                name=trim['name'],
                academic_year=academic_year,
                start_date=trim['start'],
                end_date=trim['end'],
                is_active=is_active
            )

            status = self.style.SUCCESS('✓ ACTIVE') if is_active else ''
            self.stdout.write(
                f"  ✓ {trim['display']:<20} "
                f"{trim['start'].strftime('%d/%m/%Y')} - {trim['end'].strftime('%d/%m/%Y')} "
                f"{status}"
            )

    def create_semesters(self, academic_year, start_year, end_year, activate_first):
        """Crée les 2 semestres de l'année scolaire"""
        self.stdout.write(
            self.style.SUCCESS(f'\nCréation des semestres pour {academic_year}')
        )
        self.stdout.write('-' * 70)

        semesters = [
            {
                'name': 'semestre1',
                'display': '1er Semestre',
                'start': date(start_year, 9, 1),
                'end': date(end_year, 1, 31),
            },
            {
                'name': 'semestre2',
                'display': '2e Semestre',
                'start': date(end_year, 2, 1),
                'end': date(end_year, 6, 30),
            },
        ]

        for idx, sem in enumerate(semesters):
            is_active = activate_first and idx == 0

            period = Period.objects.create(
                name=sem['name'],
                academic_year=academic_year,
                start_date=sem['start'],
                end_date=sem['end'],
                is_active=is_active
            )

            status = self.style.SUCCESS('✓ ACTIVE') if is_active else ''
            self.stdout.write(
                f"  ✓ {sem['display']:<20} "
                f"{sem['start'].strftime('%d/%m/%Y')} - {sem['end'].strftime('%d/%m/%Y')} "
                f"{status}"
            )
