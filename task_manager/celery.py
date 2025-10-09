import os
from celery import Celery
from celery.schedules import crontab


# set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

app = Celery('task_manager')

# Load settings from Django settings with a CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in Django apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-reminders-every-10-minutes': {
        'task': 'tasks.tasks.send_reminders_task',
        'schedule': crontab(minute='*/10'),  # every 10 minutes
    },
}