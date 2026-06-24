from django.apps import AppConfig


class ClientsConfig(AppConfig):
    name = 'clients'
    verbose_name = 'Clientes'

    def ready(self):
        import clients.signals  # noqa: F401
