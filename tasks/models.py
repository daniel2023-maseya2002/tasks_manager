from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", _("Admin")),
        ("user", _("User")),
    )

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        WARNED = "warned", _("Warned")
        BLOCKED = "blocked", _("Blocked")

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Status"),
        help_text=_("User account status: controls login and admin visibility"),
    )

    # Optionally: a short reason or warnings count
    warning_note = models.TextField(_("Warning note"), blank=True, null=True)

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    # 🆕 Profile fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    email_notifications = models.BooleanField(default=True)

    def block(self, reason: str = ""):
        self.status = CustomUser.Status.BLOCKED
        self.is_active = False
        if reason:
            self.warning_note = reason
        self.save(update_fields=["status", "is_active", "warning_note"])

    def warn(self, note: str = ""):
        self.status = CustomUser.Status.WARNED
        if note:
            self.warning_note = note
        self.save(update_fields=["status", "warning_note"])

    def activate(self):
        self.status = CustomUser.Status.ACTIVE
        self.is_active = True
        self.save(update_fields=["status", "is_active"])

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]


class Task(models.Model):
    STATUS_CHOICES = (
        ("Pending", _("Pending")),
        ("In Progress", _("In Progress")),
        ("Completed", _("Completed")),
    )

    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), null=True, blank=True)
    due_date = models.DateField(_("Due date"), null=True, blank=True)

    # New status fields
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default="Pending")
    is_completed = models.BooleanField(_("Is completed"), default=False)

    reminder_sent = models.BooleanField(_("Reminder sent"), default=False)
    reminder_sent_offsets = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True,
        help_text=_("List of days before due date for which reminders have already been sent")
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

    # Collaborations
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks_collaborating', blank=True)

    # New field for attachments
    attachment = models.FileField(upload_to='task_attachments/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Keep is_completed in sync with status
        self.is_completed = (self.status == "Completed")
        super().save(*args, **kwargs)

    def __str__(self):
        owner_name = self.owner.username if self.owner else _("No Owner")
        return f"{self.title} (Owner: {owner_name})"

    def is_due_soon(self):
        """Returns True if task is due within 1 day"""
        if self.due_date:
            return timezone.now().date() + timedelta(days=1) >= self.due_date
        return False

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")


class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(_("Message"), max_length=255)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(_("Read"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.message}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(_("Content"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"

    class Meta:
        ordering = ["-login_time"]
        verbose_name = _("User activity")
        verbose_name_plural = _("User activities")


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(_("OTP code"), max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        # OTP valid for 10 minutes
        return timezone.now() - self.created_at < timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Password reset OTP")
        verbose_name_plural = _("Password reset OTPs")
