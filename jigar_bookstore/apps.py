from django.apps import AppConfig


class JigarBookstoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jigar_bookstore'

    def ready(self):
        import jigar_bookstore.signals