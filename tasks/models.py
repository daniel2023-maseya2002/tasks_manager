from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return f"{self.username} ({self.role})"


class Task(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    # New status fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    is_completed = models.BooleanField(default=False)

    reminder_sent = models.BooleanField(default=False)
    reminder_sent_offsets = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True,
        help_text="List of days before due date for which reminders have already been sent"
    )

    # Relations
    owner = models.ForeignKey(
        CustomUser,
        related_name="owned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #Collaborations
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks_collaborating', blank=True)

    # New field for attachments
    attachment = models.FileField(upload_to='task_attachements/', null=True, blank=True)
    def save(self, *args, **kwargs):
        # Keep is_completed in sync with status
        self.is_completed = (self.status == "Completed")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Owner: {self.owner.username if self.owner else 'No Owner'})"
    
    def is_due_soon(self):
        """Returns True if task is due within 1 day"""
        if self.due_date:
            return timezone.now().date() + timedelta(days=1) >= self.due_date
        return False

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.message}"

class Comment(models.Model):
        task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
        author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
        content = models.TextField()
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"Comment by {self.author.username} on {self.task.title}"
        

class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        # OTP valid for 10 minutes
        return timezone.now() - self.created_at < timedelta(minutes=4)

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"
    

    