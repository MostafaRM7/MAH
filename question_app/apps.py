from django.apps import AppConfig


class QuastionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'question_app'

    def ready(self):
        import question_app.signals