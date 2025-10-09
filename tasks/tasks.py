from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Task

@shared_task
def send_reminders_task():
    tasks = Task.objects.filter(due_date__lte=timezone.now(), reminder_sent=False)
    for task in tasks:
        send_mail(
            f"Reminder: {task.title}",
            f"Your task '{task.title}' is due soon!",
            'daniel.mubu21@gmail.com',  # sender
            [task.user.email],          # recipient
        )
        task.reminder_sent = True
        task.save()
