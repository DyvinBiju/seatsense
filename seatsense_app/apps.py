from django.apps import AppConfig


class SeatsenseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seatsense_app'

    def ready(self):
        import seatsense_app.signals