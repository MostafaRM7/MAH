from django.db import models
from user_app.models import Profile


class CompositePlot(models.Model):
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    body = models.JSONField()
