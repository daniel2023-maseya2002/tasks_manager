from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, Notification

def send_task_reminders():
    today = timezone.now().date()
    reminder_days = [7, 3, 1, 0]  # days before due date

    for days_before in reminder_days:
        target_date = today + timedelta(days=days_before)

        # Skip weekends unless the task is due on weekend
        if target_date.weekday() in [5, 6] and days_before != 0:  # 5=Saturday, 6=Sunday
            continue

        tasks_due_soon = Task.objects.filter(
            due_date=target_date,
            is_completed=False
        )

        for task in tasks_due_soon:
            # Skip if reminder for this offset was already sent
            if days_before in task.reminder_sent_offsets:
                continue

            message = f"Reminder: Your task '{task.title}' is due on {task.due_date}."

            # Create in-app notification
            if task.assigned_to:
                Notification.objects.create(
                    recipient=task.assigned_to,
                    message=message,
                    task=task
                )

            # Email recipients
            recipients = []
            if task.assigned_to and task.assigned_to.email:
                recipients.append(task.assigned_to.email)
            if task.owner and task.owner.email and task.owner.email not in recipients:
                recipients.append(task.owner.email)

            if recipients:
                send_mail(
                    subject="Task Deadline Reminder",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                    fail_silently=False,
                )

            # Mark this offset as sent
            task.reminder_sent_offsets.append(days_before)
            task.save()
