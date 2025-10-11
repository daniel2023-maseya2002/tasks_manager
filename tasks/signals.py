from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Task, Notification
from tasks.utils.email_templates import send_task_notification
from django.contrib.auth import get_user_model

User = get_user_model()

# ============================================================== 
# ✅ When a task is created or completed
# ============================================================== 
@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    """
    Handle notifications when a task is created or completed.
    """
    # --- Task Created ---
    if created and instance.assigned_to:
        Notification.objects.create(
            recipient=instance.assigned_to,
            message=f"You have been assigned a new task: {instance.title}",
            task=instance
        )

        # Only send email if user opted in
        if instance.assigned_to.email_notifications:
            send_task_notification(instance.assigned_to, instance, action="assign")

    # --- Task Completed ---
    elif not created and instance.is_completed:
        Notification.objects.create(
            recipient=instance.owner,
            message=f"Your task '{instance.title}' has been marked as completed.",
            task=instance
        )

        if instance.owner.email_notifications:
            send_task_notification(instance.owner, instance, action="completed")

# ============================================================== 
# ✅ Check and notify for upcoming deadlines
# ============================================================== 
@receiver(post_save, sender=Task)
def check_upcoming_deadline(sender, instance, **kwargs):
    if instance.due_date:
        today = timezone.now().date()
        if instance.due_date == today + timedelta(days=1) and not instance.is_completed:
            recipient = instance.assigned_to or instance.owner
            Notification.objects.create(
                recipient=recipient,
                message=f"Reminder: Task '{instance.title}' is due tomorrow!",
                task=instance
            )
            if recipient.email_notifications:
                send_task_notification(recipient, instance, action="reminder")

# ============================================================== 
# ✅ Notify collaborators when added or removed
# ============================================================== 
@receiver(m2m_changed, sender=Task.collaborators.through)
def collaborators_changed(sender, instance, action, pk_set, **kwargs):
    # --- Collaborators added ---
    if action == "post_add":
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                Notification.objects.create(
                    recipient=user,
                    message=f"You have been added as a collaborator on the task: {instance.title}",
                    task=instance
                )
                if user.email_notifications:
                    send_task_notification(user, instance, action="collaborator_added")
            except User.DoesNotExist:
                pass

    # --- Collaborators removed ---
    elif action == "post_remove":
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                Notification.objects.create(
                    recipient=user,
                    message=f"You have been removed from the task: {instance.title}",
                    task=instance
                )
                if user.email_notifications:
                    send_task_notification(user, instance, action="collaborator_removed")
            except User.DoesNotExist:
                pass
