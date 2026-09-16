from django.core.management.base import BaseCommand
from django.db import transaction

from school_finance.models import Payment, PaymentInstallment, Receipt


class Command(BaseCommand):
    help = (
        "Affiche le dernier reçu émis et détecte les versements/paiements "
        "sans reçu (créés avec succès mais dont le reçu n'a pas pu être "
        "généré à cause du bug de numérotation). Sans --apply, la commande "
        "ne fait qu'un état des lieux."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help="Créer réellement les reçus manquants (sinon: simulation)."
        )

    def handle(self, *args, **options):
        apply_changes = options['apply']

        last_receipt = Receipt.objects.order_by('-created_at').first()
        if last_receipt:
            student = last_receipt.payment.student
            self.stdout.write(
                f"Dernier reçu émis: {last_receipt.receipt_number} "
                f"le {last_receipt.created_at:%Y-%m-%d %H:%M} - "
                f"{student.name} {student.first_name} - "
                f"{last_receipt.amount} FCFA (paiement #{last_receipt.payment_id})"
            )
        else:
            self.stdout.write("Aucun reçu trouvé dans la base.")

        self.stdout.write("")

        # Versements existants sans reçu associé
        missing_installments = PaymentInstallment.objects.filter(
            receipts__isnull=True
        ).select_related('payment', 'payment__student').order_by('created_at')

        count = missing_installments.count()
        self.stdout.write(f"Versements sans reçu: {count}")

        for inst in missing_installments:
            student = inst.payment.student
            self.stdout.write(
                f"  - Versement #{inst.pk} (paiement #{inst.payment_id}) "
                f"{student.name} {student.first_name} - {inst.amount} FCFA "
                f"le {inst.payment_date} (créé le {inst.created_at:%Y-%m-%d %H:%M})"
            )
            if apply_changes:
                with transaction.atomic():
                    receipt = Receipt.objects.create(
                        payment=inst.payment,
                        installment=inst,
                        amount=inst.amount,
                        issued_by=inst.received_by or 'Régularisation',
                        notes="Reçu généré rétroactivement (bug de numérotation corrigé).",
                    )
                self.stdout.write(f"      -> Reçu créé: {receipt.receipt_number}")

        # Paiements sans aucun versement (le tout premier appel a échoué avant l'installment)
        orphan_payments = Payment.objects.filter(installments__isnull=True)
        orphan_count = orphan_payments.count()
        if orphan_count:
            self.stdout.write(f"\nPaiements sans aucun versement ni reçu: {orphan_count}")
            for payment in orphan_payments.select_related('student'):
                self.stdout.write(
                    f"  - Paiement #{payment.pk} {payment.student.name} "
                    f"{payment.student.first_name} - {payment.paid_amount} FCFA "
                    f"le {payment.payment_date}"
                )

        if not apply_changes and (count or orphan_count):
            self.stdout.write(
                self.style.WARNING(
                    "\nMode simulation : aucun reçu créé. "
                    "Relancez avec --apply pour générer les reçus manquants."
                )
            )
        elif apply_changes:
            self.stdout.write(self.style.SUCCESS("\nRégularisation terminée."))
