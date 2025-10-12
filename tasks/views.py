import random
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, TaskForm, CommentForm, CustomUserUpdateForm, UserEditForm
from .models import Task, CustomUser, Notification, Comment, UserActivity, PasswordResetOTP
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date, timedelta
from .utils.email_templates import send_task_notification
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from .ai_service import generate_task_summary
from .ai_utils import generate_task_summary



User = get_user_model()

# Create your views here.
def signup_view(request):
    """Register new users."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("tasks:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "tasks/signup.html", {"form": form})


class MyLoginView(LoginView):
    template_name = "tasks/login.html"

    def form_valid(self, form):
        """When login succeeds, record user activity."""
        user = form.get_user()
        response = super().form_valid(form)

        # Record login details
        UserActivity.objects.create(
            user=user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', 'Unknown'),
            login_time=timezone.now(),
        )

        return response


def my_logout_view(request):
    """Logout user via GET and redirect to login page."""
    logout(request)
    return redirect(reverse_lazy("tasks:login"))



@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    # 🧭 Tasks: all for superuser, filtered for normal users
    if user.is_superuser:
        tasks = Task.objects.all().order_by('-created_at')
    else:
        tasks = Task.objects.filter(Q(owner=user) | Q(assigned_to=user)).distinct().order_by('-created_at')

    # 📊 Task summary counts
    pending_count = tasks.filter(status="Pending").count()
    in_progress_count = tasks.filter(status="In Progress").count()
    completed_count = tasks.filter(status="Completed").count()

    # ⏰ Upcoming tasks (due today or tomorrow, not completed)
    upcoming_tasks = tasks.filter(
        due_date__lte=tomorrow,
        is_completed=False
    )

    # 🔔 Latest 5 notifications for this user
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]

    context = {
        "tasks": tasks,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "upcoming_tasks": upcoming_tasks,
        "notifications": notifications,
    }

    return render(request, "tasks/dashboard.html", context)

@login_required
def task_list(request):
    # Start with all tasks
    tasks = Task.objects.all()

    # Get filter parameters from GET request
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    assigned_to = request.GET.get("assigned_to", "").strip()

    # Admin sees all tasks, normal users see only their own or assigned ones
    if not (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        tasks = tasks.filter(Q(owner=request.user) | Q(assigned_to=request.user))

    # ✅ Filter by status
    if status:
        # Case-insensitive match for the status field
        tasks = tasks.filter(status__iexact=status)

    # ✅ Filter by assigned_to username (case-insensitive)
    if assigned_to:
        tasks = tasks.filter(assigned_to__username__icontains=assigned_to)

    # ✅ Filter by title or description
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Order newest first
    tasks = tasks.order_by("-created_at")

    context = {
        "tasks": tasks,
        "search_query": search,
        "status_filter": status,
        "assigned_to_filter": assigned_to,
    }

    return render(request, "tasks/task_list.html", context)


# Create a task
@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            form.save_m2m()
            messages.success(request, "Task created successfully!")
            return redirect("tasks:task_list")
    else:
        form = TaskForm(user=request.user)
    return render(request, "tasks/task_form.html", {"form": form})



#update a task
@login_required
def task_update(request, pk):
    """Update a task — only admin, owner, or assigned user can edit."""
    task = get_object_or_404(Task, pk=pk)

    # ✅ Permission check
    if not (request.user.is_superuser or request.user == task.owner or request.user == task.assigned_to):
        messages.error(request, "You don’t have permission to edit this task.")
        return redirect("dashboard")

    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES, instance=task, user=request.user)
        if form.is_valid():
            # ✅ Save model instance first (without committing M2M)
            updated_task = form.save(commit=False)
            updated_task.owner = task.owner  # Keep existing owner
            updated_task.save()

            # ✅ Now save collaborators (ManyToManyField)
            form.save_m2m()

            messages.success(request, "Task updated successfully!")
            return redirect("tasks:task_list")
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, "tasks/task_form.html", {"form": form, "task": task})



@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # ✅ Permission check
    if not (request.user.is_superuser or request.user == task.owner or request.user == task.assigned_to):
        messages.error(request, "You do not have permission to change this task.")
        return redirect('tasks:task_list')

    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = ["Pending", "In Progress", "Completed"]

        if new_status in valid_statuses:
            old_status = task.status
            if new_status != old_status:
                task.status = new_status
                task.is_completed = (new_status == "Completed")
                task.save()

                messages.success(request, f"Task '{task.title}' status updated to {new_status}.")

                # ✅ Create notification for assigned user (if not the updater)
                if task.assigned_to and task.assigned_to != request.user:
                    Notification.objects.create(
                        recipient=task.assigned_to,
                        task=task,
                        message=f"The status of your assigned task '{task.title}' changed from '{old_status}' to '{new_status}'."
                    )

                # ✅ Optional: notify task owner if someone else changed the status
                if task.owner and task.owner != request.user:
                    Notification.objects.create(
                        recipient=task.owner,
                        task=task,
                        message=f"The task '{task.title}' you created was updated to '{new_status}' by {request.user.username}."
                    )

            else:
                messages.info(request, "No status change detected.")
        else:
            messages.error(request, "Invalid status selected.")

        return redirect('tasks:task_list')

    return render(request, "tasks/update_task_status.html", {"task": task})



#delete a task
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Only owner or admin can delete
    if not (request.user.is_superuser or task.assigned_to == request.user):
        messages.error(request, "You don’t have permission to delete this task.")
        return redirect("dashboard")
    if request.method == "POST":
        task.delete()
        return redirect("tasks:task_list")

    # FIX: should be "tasks/task_confirm_delete.html"
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


# Utility to check if user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff



# Admin: View All users
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    # Get search and role filter parameters
    search_query = request.GET.get("search", "")
    role_filter = request.GET.get("role", "")

    # Get all users
    users = CustomUser.objects.all()

    # Filter by username (case-insensitive)
    if search_query:
        users = users.filter(username__icontains=search_query)

    # Filter by role using is_staff
    if role_filter:
        if role_filter.lower() == "admin":
            users = users.filter(is_staff=True)
        elif role_filter.lower() == "user":
            users = users.filter(is_staff=False)

    context = {
        "users": users,
        "search_query": search_query,
        "role_filter": role_filter,
    }

    return render(request, "tasks/manage_users.html", context)


# Admin create a new user
@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "user" # default
            user.save()
            messages.success(request, "User created successfully!")
            return redirect("tasks:manage_users")
        
    else:
        form = CustomUserCreationForm()
    return render(request, "tasks/create_user.html", {"form": form})



@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect("tasks:manage_users")
    else:
        form = CustomUserUpdateForm(instance=user)

    return render(request, "tasks/edit_user.html", {"form": form, "user": user})


# Admin: Delete user
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(request, user_id)
    user.delete()
    messages.success(request, "User Deleted Successfully!")
    return redirect("tasks:manage_users")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def redirect_admin_users(request):
    return redirect("tasks:manage_users")


@login_required
def delete_user(request, user_id):

    #Allow only rel admins or superuser
    if not (request.user.is_superuser or request.user.role == "admin"):
        raise PermissionDenied
    
    user_obj = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "User deleted succefully!")
        return redirect("tasks:manage_users")
    
    # for Get show the confirmation page
    return render(request, "tasks/delete_user.html", {"user_obj": user_obj})


# Only admins can access
@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, "user_list.html", {'users': users})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('tasks:notification_view')  # back to notification page

@login_required
def notification_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    # Mark all unread as read automatically
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    return render(request, "tasks/notifications.html", {"notifications": notifications})

@login_required
def unread_count_api(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def mark_all_notifications_read(request):
    """Mark all user notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications_view')

@login_required
def task_detail(request, pk):
    """Display a single task with comments and allow posting new comments."""

    task = get_object_or_404(Task, pk=pk)

    # ✅ Permission check: owner, assigned user, collaborator, or admin
    if not (
        request.user == task.owner
        or request.user == task.assigned_to
        or request.user in task.collaborators.all()
        or request.user.role == 'admin'
    ):
        return HttpResponseForbidden("You do not have permission to view this task.")

    # Fetch comments ordered by newest first
    comments = task.comments.all().order_by('-created_at')

    # Handle new comment submission
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect('tasks:task_detail', pk=pk)
    else:
        form = CommentForm()

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'comments': comments,
        'form': form
    })



@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        task = instance.task
        commenter = instance.author
        owner = task.owner

        #Notify the task owner only the commenter isn't the owner
        if owner != commenter:
            Notification.objects.create(
                recipient=owner,
                message=f"{commenter.username} commented on '{task.title}': {instance.content[:50]}...",
                task=task
            )

@login_required
def calendar_view(request):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday

    # ✅ Fetch tasks due between Monday and Sunday
    tasks = (
        Task.objects.filter(
            due_date__range=[start_of_week, end_of_week],
            owner=request.user
        ) |
        Task.objects.filter(
            due_date__range=[start_of_week, end_of_week],
            assigned_to=request.user
        )
    )

    # ✅ Group tasks by day
    tasks_by_date = {}
    for day in range(7):
        current_date = start_of_week + timedelta(days=day)
        tasks_by_date[current_date] = tasks.filter(due_date=current_date)

    context = {
        "tasks_by_date": tasks_by_date,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
    }
    return render(request, "tasks/calendar.html", context)


@login_required
def calendar_view(request):
    user = request.user

    # Get week offset from query params (default=0)
    try:
        week_offset = int(request.GET.get('week_offset', 0))
    except ValueError:
        week_offset = 0

    today = timezone.now().date()
    # Adjust today based on week_offset
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    # Fetch tasks for the user within the week
    tasks = Task.objects.filter(
        Q(owner=user) | Q(assigned_to=user),
        due_date__range=[start_of_week, end_of_week]
    )

    # Group tasks by date
    tasks_by_date = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        tasks_by_date[day] = tasks.filter(due_date=day)

    context = {
        "tasks_by_date": tasks_by_date,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "week_offset": week_offset,  # pass offset for navigation
    }
    return render(request, "tasks/calendar.html", context)

@user_passes_test(lambda u: u.is_superuser or getattr(u, "role", "") == "admin")
def reports_view(request):
    # 1️⃣ Task statistics
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(Q(status="completed") | Q(is_completed=True)).count()
    pending_tasks = Task.objects.filter(Q(status="pending") | Q(is_completed=False)).count()
    in_progress_tasks = Task.objects.filter(Q(status="in_progress") | Q(status="progress")).count()

    # 2️⃣ Percentages for visual charts
    def percent(part):
        return round((part / total_tasks * 100), 1) if total_tasks else 0

    completed_percent = percent(completed_tasks)
    pending_percent = percent(pending_tasks)
    in_progress_percent = percent(in_progress_tasks)

    # 3️⃣ Top 5 users (only regular users)
    top_users = (
        CustomUser.objects.filter(role="user")
        .annotate(
            completed_count=Count("owned_tasks", filter=Q(owned_tasks__status="completed") | Q(owned_tasks__is_completed=True)),
            in_progress_count=Count("owned_tasks", filter=Q(owned_tasks__status="in_progress") | Q(owned_tasks__status="progress")),
            pending_count=Count("owned_tasks", filter=Q(owned_tasks__status="pending")),
        )
        .order_by("-completed_count")[:5]
    )

    # 4️⃣ Recent user logins (last 10)
    recent_logins = UserActivity.objects.select_related("user").order_by("-login_time")[:10]

    # 5️⃣ Chart.js Data
    chart_data = {
        "labels": ["Pending", "In Progress", "Completed"],
        "data": [pending_tasks, in_progress_tasks, completed_tasks],
    }

    # 6️⃣ Context for template
    context = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_percent": completed_percent,
        "pending_percent": pending_percent,
        "in_progress_percent": in_progress_percent,
        "top_users": top_users,
        "recent_logins": recent_logins,
        "chart_data": chart_data,
    }

    return render(request, "tasks/reports.html", context)

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp_code = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=user, otp_code=otp_code)

            # Send OTP via email
            send_mail(
                'Your Password Reset OTP - Task Manager',
                f'Your OTP for resetting your password is: {otp_code}. It will expire in 4 minutes.',
                'yourapp@example.com',  # Replace with your real sender email
                [email],
                fail_silently=False,
            )

            request.session['reset_email'] = email
            messages.success(request, 'OTP sent to your email!')
            return redirect('tasks:verify_otp')

        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')

    return render(request, 'tasks/forgot_password.html')

def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('tasks:forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            user = User.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(user=user).latest('created_at')

            if otp_record.otp_code == otp_input and otp_record.is_valid():
                request.session['otp_verified'] = True
                messages.success(request, 'OTP verified successfully!')
                return redirect('tasks:reset_password')
            else:
                messages.error(request, 'Invalid or expired OTP.')

        except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
            messages.error(request, 'Invalid request.')

    return render(request, 'tasks/verify_otp.html')

def reset_password_view(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')

    if not (email and otp_verified):
        messages.error(request, 'Unauthorized action.')
        return redirect('tasks:forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('tasks:forgot_password')

            # ✅ Use Django's built-in secure method
            user.set_password(password1)
            user.save()

            # Clean session
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)

            messages.success(request, 'Password reset successfully! You can now log in.')
            return redirect('tasks:login')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'tasks/reset_password.html')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('tasks:profile')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'tasks/profile.html', {'form': form})

@login_required
def settings_view(request):
    user = request.user  # CustomUser instance

    if request.method == "POST":
        # Update editable fields
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")
        user.bio = request.POST.get("bio")
        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES["profile_picture"]
        user.email_notifications = request.POST.get("email_notifications") == "on"
        user.save()
        messages.success(request, "Settings updated successfully!")
        return redirect("tasks:settings")

    return render(request, "tasks/settings.html", {"user": user})

RATE_LIMIT_SECONDS = 10  # allow one request every 10s per user

@login_required
@require_POST
def ai_task_summary_view(request):
    user = request.user

    # basic per-user rate limiting
    key = f"ai_summary_rate_{user.id}"
    last = cache.get(key)
    now = time.time()
    if last and now - last < RATE_LIMIT_SECONDS:
        return JsonResponse({"error": "Too many requests. Please wait a few seconds."}, status=429)
    cache.set(key, now, RATE_LIMIT_SECONDS)

    # check for cached summary (reduce cost)
    cache_key = f"ai_summary_cache_{user.id}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"summary": cached, "cached": True})

    # Collect tasks relevant to the user
    tasks = Task.objects.filter(Q(owner=user) | Q(assigned_to=user)).order_by("due_date")

    try:
        summary = generate_task_summary(tasks)
    except Exception as e:
        return JsonResponse({"error": "AI service error"}, status=500)

    # cache summary for short time (e.g., 60 sec)
    cache.set(cache_key, summary, 60)
    return JsonResponse({"summary": summary, "cached": False})