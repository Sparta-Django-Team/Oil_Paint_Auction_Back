# celery
from __future__ import absolute_import, unicode_literals
from celery import shared_task

# users
from .models import User

@shared_task
def reset_attendance_check():
    User.objects.filter(is_attendance_check=True).update(is_attendance_check=False)