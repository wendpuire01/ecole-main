"""
Commande Django pour diagnostiquer la configuration des périodes
Usage: python manage.py check_periods
"""
from django.core.management.base import BaseCommand
from school_portal.models import Period, Assignment, Mark


class Command(BaseCommand):
    help = 'Diagnostique la configuration des périodes et identifie les problèmes'

    def handle(self, *args, **options):
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('   DIAGNOSTIC DES PÉRIODES SCOLAIRES'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # 1. Vérifier si des périodes existent
        periods_count = Period.objects.count()
        self.stdout.write(f'📊 Nombre total de périodes : {periods_count}')

        if periods_count == 0:
            self.stdout.write(self.style.ERROR(''))
            self.stdout.write(self.style.ERROR('❌ PROBLÈME: Aucune période n\'existe!'))
            self.stdout.write(self.style.ERROR(''))
            self.stdout.write('💡 SOLUTION:')
            self.stdout.write('   Créez des périodes avec la commande:')
            self.stdout.write(self.style.WARNING('   python manage.py setup_periods 2025-2026 --activate-first'))
            self.stdout.write('')
            return

        # 2. Vérifier la période active
        self.stdout.write('')
        self.stdout.write('-' * 70)
        active_period = Period.objects.filter(is_active=True).first()

        if active_period:
            self.stdout.write(self.style.SUCCESS('✅ Période active trouvée:'))
            self.stdout.write(f'   • Nom: {active_period.get_name_display()}')
            self.stdout.write(f'   • Année: {active_period.academic_year}')
            self.stdout.write(f'   • Dates: {active_period.start_date.strftime("%d/%m/%Y")} - {active_period.end_date.strftime("%d/%m/%Y")}')
        else:
            self.stdout.write(self.style.ERROR('❌ PROBLÈME: Aucune période n\'est active!'))
            self.stdout.write('')
            self.stdout.write('💡 SOLUTION:')
            self.stdout.write('   Activez une période avec:')
            self.stdout.write(self.style.WARNING('   python manage.py set_active_period --list'))
            self.stdout.write(self.style.WARNING('   python manage.py set_active_period <id>'))
            self.stdout.write('')

        # 3. Lister toutes les périodes
        self.stdout.write('')
        self.stdout.write('-' * 70)
        self.stdout.write('📋 Liste de toutes les périodes:')
        self.stdout.write('')

        periods = Period.objects.all().order_by('-academic_year', 'start_date')
        current_year = None

        for period in periods:
            if period.academic_year != current_year:
                current_year = period.academic_year
                self.stdout.write('')
                self.stdout.write(f'   Année Scolaire: {current_year}')
                self.stdout.write('   ' + '-' * 60)

            status = self.style.SUCCESS('✓ ACTIVE') if period.is_active else '  Inactive'
            self.stdout.write(
                f'   ID: {period.id:<3} | '
                f'{period.get_name_display():<20} | '
                f'{period.start_date.strftime("%d/%m/%Y")} - {period.end_date.strftime("%d/%m/%Y")} | '
                f'{status}'
            )

        # 4. Vérifier les devoirs sans période
        self.stdout.write('')
        self.stdout.write('-' * 70)
        assignments_without_period = Assignment.objects.filter(period__isnull=True).count()

        if assignments_without_period > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  ATTENTION: {assignments_without_period} devoir(s) ne sont pas associés à une période!'
                )
            )
            self.stdout.write('')
            self.stdout.write('💡 SOLUTION:')
            self.stdout.write('   Ces devoirs doivent être associés à une période.')
            self.stdout.write('   Utilisez l\'admin Django ou le shell pour corriger cela.')
            self.stdout.write('')
            self.stdout.write('   Exemple (shell):')
            self.stdout.write(self.style.WARNING('   python manage.py shell'))
            self.stdout.write(self.style.WARNING('   >>> from school_portal.models import Assignment, Period'))
            self.stdout.write(self.style.WARNING('   >>> period = Period.objects.get(id=1)'))
            self.stdout.write(self.style.WARNING('   >>> Assignment.objects.filter(period__isnull=True).update(period=period)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Tous les devoirs sont associés à une période'))

        # 5. Statistiques par période
        self.stdout.write('')
        self.stdout.write('-' * 70)
        self.stdout.write('📈 Statistiques par période:')
        self.stdout.write('')

        for period in periods:
            assignments = Assignment.objects.filter(period=period).count()
            marks = Mark.objects.filter(assignment__period=period).count()

            self.stdout.write(f'   {period.get_name_display()} ({period.academic_year}):')
            self.stdout.write(f'      • Devoirs/Compositions: {assignments}')
            self.stdout.write(f'      • Notes enregistrées: {marks}')
            self.stdout.write('')

        # 6. Recommandations
        self.stdout.write('-' * 70)
        self.stdout.write('💡 RECOMMANDATIONS:')
        self.stdout.write('')

        if not active_period:
            self.stdout.write('   1. ❌ Activez une période pour que les bulletins fonctionnent correctement')
        else:
            self.stdout.write('   1. ✅ Une période est active')

        if assignments_without_period > 0:
            self.stdout.write('   2. ❌ Associez tous les devoirs à leur période respective')
        else:
            self.stdout.write('   2. ✅ Tous les devoirs sont associés à une période')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('   FIN DU DIAGNOSTIC'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
