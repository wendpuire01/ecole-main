from django.apps import AppConfig


class SchoolPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school_portal'

    def ready(self):
        import school_portal.signals  # noqa
