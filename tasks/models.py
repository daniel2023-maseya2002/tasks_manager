from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return f"{self.username} ({self.role})"
    
CustomUser = get_user_model()

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    #Relation

    owner = models.ForeignKey(
        CustomUser,
        related_name="owned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    ) # user who created it

    assigned_to = models.ForeignKey(
        CustomUser,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    ) # optional: admin assigns

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (Owner: {self.owner.username})"