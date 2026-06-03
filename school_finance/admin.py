from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AcademicYear, FeeType, FeeStructure, PaymentSchedule, Enrollment,
    PaymentMethod, Payment, PaymentInstallment,
    StudentAccount, Receipt
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active_badge', 'created_at']
    list_filter = ['is_active', 'start_date']
    search_fields = ['name']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: gray;">Inactive</span>')
    is_active_badge.short_description = 'Statut'


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_mandatory', 'is_active', 'created_at']
    list_filter = ['category', 'is_mandatory', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


class PaymentScheduleInline(admin.TabularInline):
    model = PaymentSchedule
    extra = 0
    fields = ['period', 'expected_amount', 'due_date']


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ['fee_structure', 'period', 'expected_amount_fmt', 'due_date']
    list_filter = ['period', 'fee_structure__academic_year', 'fee_structure__class_level']
    search_fields = ['fee_structure__fee_type__name', 'fee_structure__class_level__name']

    def expected_amount_fmt(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.expected_amount)
    expected_amount_fmt.short_description = 'Montant attendu'


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['fee_type', 'class_level', 'academic_year', 'amount_formatted', 'payment_frequency', 'is_active_badge']
    list_filter = ['academic_year', 'class_level', 'fee_type__category', 'payment_frequency', 'is_active']
    search_fields = ['fee_type__name', 'class_level__name']
    date_hierarchy = 'created_at'
    ordering = ['academic_year', 'class_level', 'fee_type']
    inlines = [PaymentScheduleInline]
    actions = ['activate_structures', 'deactivate_structures']

    def amount_formatted(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.amount)
    amount_formatted.short_description = 'Montant'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;font-weight:bold;">✓ Actif</span>')
        return format_html('<span style="color:red;">✗ Inactif</span>')
    is_active_badge.short_description = 'Statut'

    def activate_structures(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} structure(s) activée(s).')
    activate_structures.short_description = 'Activer les frais sélectionnés'

    def deactivate_structures(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} structure(s) désactivée(s).')
    deactivate_structures.short_description = 'Désactiver les frais sélectionnés'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'class_enrolled', 'academic_year', 'enrollment_type_badge',
                    'enrollment_fee_formatted', 'enrollment_date', 'status_badge']
    list_filter = ['academic_year', 'class_enrolled', 'enrollment_type', 'status', 'enrollment_date']
    search_fields = ['student__name', 'student__first_name', 'student__surname']
    date_hierarchy = 'enrollment_date'
    ordering = ['-enrollment_date']

    def student_name(self, obj):
        return f"{obj.student.name} {obj.student.first_name}"
    student_name.short_description = 'Étudiant'

    def enrollment_type_badge(self, obj):
        colors = {
            'new': 'blue',
            'renewal': 'green',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.enrollment_type, 'gray'),
            obj.get_enrollment_type_display()
        )
    enrollment_type_badge.short_description = 'Type'

    def enrollment_fee_formatted(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.enrollment_fee)
    enrollment_fee_formatted.short_description = 'Frais'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method_type', 'is_active', 'created_at']
    list_filter = ['method_type', 'is_active']
    search_fields = ['name']


class PaymentInstallmentInline(admin.TabularInline):
    model = PaymentInstallment
    extra = 0
    fields = ['installment_number', 'amount', 'payment_date', 'payment_method', 'reference_number', 'received_by']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'fee_type', 'total_amount_formatted', 'paid_amount_formatted',
                    'remaining_formatted', 'payment_date', 'status_badge', 'payment_percentage_bar']
    list_filter = ['academic_year', 'fee_type', 'status', 'payment_method', 'payment_date', 'period']
    search_fields = ['student__name', 'student__first_name', 'reference_number', 'transaction_id']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    readonly_fields = ['remaining_amount', 'is_fully_paid', 'payment_percentage']
    inlines = [PaymentInstallmentInline]

    fieldsets = (
        ('Informations Étudiant', {
            'fields': ('student', 'academic_year', 'fee_type')
        }),
        ('Montants', {
            'fields': ('total_amount', 'paid_amount', 'remaining_amount', 'payment_percentage')
        }),
        ('Détails du Paiement', {
            'fields': ('payment_method', 'payment_date', 'period', 'reference_number', 'transaction_id')
        }),
        ('Statut et Notes', {
            'fields': ('status', 'received_by', 'notes')
        }),
    )

    def student_name(self, obj):
        return f"{obj.student.name} {obj.student.first_name}"
    student_name.short_description = 'Étudiant'

    def total_amount_formatted(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.total_amount)
    total_amount_formatted.short_description = 'Total'

    def paid_amount_formatted(self, obj):
        color = 'green' if obj.is_fully_paid else 'orange'
        return format_html('<span style="color: {};">{:,.0f} FCFA</span>', color, obj.paid_amount)
    paid_amount_formatted.short_description = 'Payé'

    def remaining_formatted(self, obj):
        remaining = obj.remaining_amount
        color = 'green' if remaining == 0 else 'red'
        return format_html('<span style="color: {};">{:,.0f} FCFA</span>', color, remaining)
    remaining_formatted.short_description = 'Reste'

    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'partial': 'orange',
            'completed': 'green',
            'cancelled': 'red',
            'refunded': 'purple',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def payment_percentage_bar(self, obj):
        percentage = obj.payment_percentage
        color = 'green' if percentage == 100 else 'orange' if percentage > 0 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center; border-radius: 3px; padding: 2px;">'
            '{}%</div></div>',
            percentage, color, int(percentage)
        )
    payment_percentage_bar.short_description = 'Progression'


@admin.register(PaymentInstallment)
class PaymentInstallmentAdmin(admin.ModelAdmin):
    list_display = ['payment_student', 'installment_number', 'amount_formatted', 'payment_date',
                    'payment_method', 'received_by']
    list_filter = ['payment_date', 'payment_method']
    search_fields = ['payment__student__name', 'reference_number']
    date_hierarchy = 'payment_date'
    ordering = ['payment', 'installment_number']

    def payment_student(self, obj):
        return f"{obj.payment.student.name} {obj.payment.student.first_name}"
    payment_student.short_description = 'Étudiant'

    def amount_formatted(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.amount)
    amount_formatted.short_description = 'Montant'


@admin.register(StudentAccount)
class StudentAccountAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'academic_year', 'total_fees_formatted', 'total_paid_formatted',
                    'balance_formatted', 'last_payment_date', 'payment_percentage_bar']
    list_filter = ['academic_year', 'last_payment_date']
    search_fields = ['student__name', 'student__first_name']
    readonly_fields = ['balance', 'payment_percentage']
    ordering = ['student']

    def student_name(self, obj):
        return f"{obj.student.name} {obj.student.first_name}"
    student_name.short_description = 'Étudiant'

    def total_fees_formatted(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.total_fees)
    total_fees_formatted.short_description = 'Total Frais'

    def total_paid_formatted(self, obj):
        return format_html('<span style="color: green;">{:,.0f} FCFA</span>', obj.total_paid)
    total_paid_formatted.short_description = 'Total Payé'

    def balance_formatted(self, obj):
        balance = obj.balance
        color = 'green' if balance == 0 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{:,.0f} FCFA</span>', color, balance)
    balance_formatted.short_description = 'Solde'

    def payment_percentage_bar(self, obj):
        percentage = obj.payment_percentage
        color = 'green' if percentage == 100 else 'orange' if percentage > 0 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center; border-radius: 3px; padding: 2px;">'
            '{}%</div></div>',
            percentage, color, int(percentage)
        )
    payment_percentage_bar.short_description = 'Progression'

    actions = ['update_account_totals']

    def update_account_totals(self, request, queryset):
        count = 0
        for account in queryset:
            account.update_totals()
            count += 1
        self.message_user(request, f"{count} compte(s) mis à jour avec succès.")
    update_account_totals.short_description = "Mettre à jour les totaux"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment_student', 'amount_formatted', 'issue_date', 'issued_by']
    list_filter = ['issue_date']
    search_fields = ['receipt_number', 'payment__student__name', 'issued_by']
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    readonly_fields = ['receipt_number', 'issue_date']

    def payment_student(self, obj):
        return f"{obj.payment.student.name} {obj.payment.student.first_name}"
    payment_student.short_description = 'Étudiant'

    def amount_formatted(self, obj):
        return format_html('<strong>{:,.0f} FCFA</strong>', obj.amount)
    amount_formatted.short_description = 'Montant'
