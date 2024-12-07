from django.apps import AppConfig

class ApplicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application"  # Remplacez par le nom réel de votre application

    def ready(self):
        import application.signals  # Import des signaux


