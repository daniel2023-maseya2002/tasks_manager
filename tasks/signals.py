from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Task, Notification
from tasks.utils.email_templates import send_task_notification  # ✅ import email sender


@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    """
    Handle notifications when a task is created or completed.
    """
    if created and instance.assigned_to:
        # In-app notification
        Notification.objects.create(
            recipient=instance.assigned_to,
            message=f"You have been assigned a new task: {instance.title}",
            task=instance
        )

        # Email notification
        send_task_notification(instance.assigned_to, instance, action="assign")

    elif not created and instance.is_completed:
        # In-app notification for owner
        Notification.objects.create(
            recipient=instance.owner,
            message=f"Your task '{instance.title}' has been marked as completed.",
            task=instance
        )

        # Email notification for owner
        send_task_notification(instance.owner, instance, action="completed")


@receiver(post_save, sender=Task)
def check_upcoming_deadline(sender, instance, **kwargs):
    """
    Check and notify if a task is due tomorrow.
    """
    if instance.due_date:
        today = timezone.now().date()
        if instance.due_date == today + timedelta(days=1) and not instance.is_completed:
            Notification.objects.create(
                recipient=instance.assigned_to or instance.owner,
                message=f"Reminder: Task '{instance.title}' is due tomorrow!",
                task=instance
            )

            # Email notification for deadline reminder
            send_task_notification(instance.assigned_to or instance.owner, instance, action="reminder")
