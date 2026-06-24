from django.apps import AppConfig


class InsurersConfig(AppConfig):
    name = 'insurers'
    verbose_name = 'Seguradoras'

    def ready(self):
        import insurers.signals  # noqa: F401
