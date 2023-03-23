from __future__ import absolute_import, unicode_literals

# celery
from celery import Celery

# python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_back.settings")

app = Celery("project_back")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
