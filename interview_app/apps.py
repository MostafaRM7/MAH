from django.apps import AppConfig


class InterviewAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interview_app'


    # def ready(self):
    #     import interview_app.signals
