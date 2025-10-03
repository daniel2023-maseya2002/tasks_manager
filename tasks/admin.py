from django.contrib import admin
from .models import CustomUser, Task
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "assigned_to", "due_date", "is_completed")
    list_filter = ("is_completed", "due_date")
    search_fields = ("title", "description")
