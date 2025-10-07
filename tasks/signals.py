from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, Notification

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        # notify assigned user
        Notification.objects.create(
            recipient=instance.assigned_to,
            message=f"You have been assigned a nes task: {instance.title}",
            task=instance
        )
    elif not created and instance.is_completed:
        #Notify owner that tasks was completed
        Notification.objects.create(
            recipient=instance.owner,
            message=f"Tour task '{instance.title}' has been marked as completed.",
            task=instance
        )