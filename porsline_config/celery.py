import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'porsline_config.settings')
app = Celery('porsline_config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
