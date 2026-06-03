from django.apps import AppConfig


class SchoolFinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school_finance'

    def ready(self):
        import school_finance.signals  # noqa
