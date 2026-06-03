from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum

from school_finance.models import PaymentSchedule, Payment
from main.notifications import notify_admins
from main.models import Notification


class Command(BaseCommand):
    help = "Vérifie les paiements en retard et génère des alertes"

    def handle(self, *args, **options):
        today = timezone.now().date()
        count = 0

        overdue_schedules = PaymentSchedule.objects.filter(
            due_date__lt=today,
            fee_structure__is_active=True,
        ).select_related(
            'fee_structure__class_level',
            'fee_structure__fee_type',
            'fee_structure__academic_year',
        )

        for schedule in overdue_schedules:
            fs = schedule.fee_structure
            students = fs.class_level.students.all()

            for student in students:
                paid = Payment.objects.filter(
                    student=student,
                    academic_year=fs.academic_year,
                    fee_type=fs.fee_type,
                    period=schedule.period,
                    status__in=['partial', 'completed'],
                ).aggregate(total=Sum('paid_amount'))['total'] or 0

                if paid < schedule.expected_amount:
                    reste = schedule.expected_amount - paid
                    nom = f"{student.name} {student.first_name}"

                    # Éviter les doublons : pas de nouvelle alerte si une non-lue existe déjà aujourd'hui
                    already = Notification.objects.filter(
                        notif_type='overdue',
                        title__contains=nom,
                        created_at__date=today,
                        is_read=False,
                    ).exists()

                    if not already:
                        notify_admins(
                            'overdue',
                            f"Retard — {nom}",
                            f"{nom} doit encore {reste:,.0f} FCFA ({schedule.get_period_display()})",
                        )
                        count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} alerte(s) de retard générée(s)."))
