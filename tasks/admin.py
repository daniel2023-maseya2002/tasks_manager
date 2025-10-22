from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Task


# ----------------------
# Admin actions
# ----------------------

@admin.action(description=_("Block selected users"))
def block_users(modeladmin, request, queryset):
    for user in queryset:
        if user.is_superuser:
            messages.warning(request, _("Cannot block a superuser: %(user)s") % {"user": user})
            continue
        user.block(reason=_("Blocked by admin: bulk action"))
    messages.success(request, _("Selected users have been blocked."))


@admin.action(description=_("Mark selected users as warned"))
def warn_users(modeladmin, request, queryset):
    for user in queryset:
        user.warn(note=_("Warning issued by admin"))
    messages.success(request, _("Selected users have been flagged as warned."))


@admin.action(description=_("Unblock / Activate selected users"))
def activate_users(modeladmin, request, queryset):
    for user in queryset:
        user.activate()
    messages.success(request, _("Selected users have been activated."))


# ----------------------
# CustomUser Admin
# ----------------------

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Role & Status"), {"fields": ("role", "status", "warning_note")}),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "status",
        "is_staff",
        "is_superuser",
    )

    list_filter = ("status", "is_staff", "is_superuser", "is_active")
    actions = [block_users, warn_users, activate_users]


# ----------------------
# Task Admin
# ----------------------

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "assigned_to", "due_date", "is_completed")
    list_filter = ("is_completed", "due_date")
    search_fields = ("title", "description")
